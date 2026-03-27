# Bibliotecas ==========================
import time
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# CONFIGURAÇÕES DO POSTGRESQL ===========
PG_CONFIG = {
    "host": "localhost",
    "database": "Destilaria",
    "user": "VS_Destilaria",
    "password": "LoboMau*86",
    "port": 5432,
}

def get_conn():
    return psycopg2.connect(**PG_CONFIG)

# ==============================================
# INTERPRETAÇÃO DOS TÓPICOS REAIS DO SIMULADOR

def interpretar_topico(topico: str):
    partes = topico.split("/")

    # Exemplo:
    # destilaria/fermentacao/Dorna_01/temperatura_pv
    # destilaria/fermentacao/geral/vazao_mosto
    # destilaria/destilacao/colunaA/temperatura_fundo
    # destilaria/utilidades/agua/temperatura_entrada

    if len(partes) < 3:
        return None

    _, area, *resto = partes

    # ---------------------------
    # FERMENTAÇÃO
    # ---------------------------
    if area == "fermentacao":

        # Caso 1: Dorna_01/temperatura_pv
        if len(resto) == 2 and resto[0].startswith("Dorna_"):
            return {
                "tabela": "curated.fermentacao",
                "equipamento": resto[0],   # Dorna_01
                "variavel": resto[1]
            }

        # Caso 2: geral/vazao_mosto
        if len(resto) == 2 and resto[0] == "geral":
            return {
                "tabela": "curated.fermentacao",
                "equipamento": "geral",
                "variavel": resto[1]
            }

    # ---------------------------
    # DESTILAÇÃO
    # ---------------------------
    if area == "destilacao":

        # colunaA/temperatura_fundo
        if len(resto) == 2 and resto[0].startswith("coluna"):
            return {
                "tabela": "curated.destilacao",
                "equipamento": resto[0],  # colunaA ou colunaB
                "variavel": resto[1]
            }

    # ---------------------------
    # UTILIDADES
    # ---------------------------
    if area == "utilidades":

        # vapor/pressao
        # agua/temperatura_entrada
        # energia/consumo
        if len(resto) == 2:
            return {
                "tabela": "curated.utilidades",
                "equipamento": resto[0],
                "variavel": resto[1]
            }

    return None

# ============================================
# INSERÇÃO NAS TABELAS CURATED

UNIDADES = {
    # Fermentação
    "temperatura_pv": "°C",
    "nivel_pv": "%",
    "ph_pv": "pH",
    "condutividade_pv": "µS/cm",
    "densidade_pv": "°Brix",
    "vazao_mosto": "m³/h",
    "vazao_ar": "Nm³/h",
    "pressao_co2": "bar",

    # Destilação
    "temperatura_fundo": "°C",
    "temperatura_inferior": "°C",
    "temperatura_media": "°C",
    "temperatura_superior": "°C",
    "temperatura_saida": "°C",
    "pressao_topo": "kPa",
    "pressao_fundo": "kPa",
    "nivel_vinho": "%",
    "nivel_flegma": "%",
    "nivel_etanol": "%",
    "nivel_fundo_coluna": "%",
    "nivel_tambor_refluxo": "%",
    "vazao_vapor": "m³/h",
    "vazao_refluxo": "m³/h",
    "vazao_alcool": "m³/h",
    "vazao_destilado": "m³/h",
    "teor_alcool": "% v/v",

    # Utilidades
    "pressao": "bar",
    "temperatura_entrada": "°C",
    "temperatura_saida": "°C",
    "vazao_resfriamento": "m³/h",
    "nivel_tq.fria": "%",
    "nivel_tq.quente": "%",
    "consumo_eletrico": "kWh",
}

#============================================================
# Tratamento dos dados a serem inseridos nas tabelas curated

def inserir_curated(cur, meta, payload, timestamp_utc, recebido_em):

    # -----------------------------
    # 1. Normalização da variável
    # -----------------------------
    variavel = meta["variavel"]

    if "_" in variavel:
        variavel_base, variavel_tipo = variavel.split("_", 1)
    else:
        variavel_base = variavel
        variavel_tipo = None

    # -----------------------------
    # 2. Unidade automática
    # -----------------------------
    unidade = UNIDADES.get(variavel, "")

    # -----------------------------
    # 3. Normalização de data/hora
    # -----------------------------
    data_utc = timestamp_utc.date()
    hora_utc = timestamp_utc.time().replace(microsecond=0)

    data_recebido = recebido_em.date()
    hora_recebido = recebido_em.time().replace(microsecond=0)

    # -----------------------------
    # 4. Tabela correta
    # -----------------------------
    tabela = meta["tabela"]  

    # -----------------------------
    # 5. SQL final
    # -----------------------------
    sql = f"""
        INSERT INTO {tabela}
            (equipamento, variavel_base, variavel_tipo, valor, 
            unidade, qualidade, data_utc, hora_utc, data_recebido, hora_recebido)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    params = (
        meta["equipamento"],
        variavel_base,
        variavel_tipo,
        payload.get("valor"),
        unidade,
        payload.get("qualidade"),
        data_utc,
        hora_utc,
        data_recebido,
        hora_recebido
    )

    cur.execute(sql, params)

# =================================================
# LOOP PRINCIPAL DO ETL CURATED

def etl_curated_loop():

    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT COALESCE(MAX(id), 0) AS last_id FROM raw.medidas_brutas_destilaria;")
    last_id = cur.fetchone()["last_id"]

    print(f"[ETL CURATED] Iniciando a partir do id {last_id}")

    try:
        while True:

            cur.execute("""
                SELECT id, timestamp_utc, topico, payload_raw, recebido_em
                FROM raw.medidas_brutas_destilaria
                WHERE id > %s
                ORDER BY id
                LIMIT 1000;
            """, (last_id,))

            rows = cur.fetchall()

            if not rows:
                time.sleep(2)
                continue

            for row in rows:
                rid = row["id"]
                topico = row["topico"]
                payload = row["payload_raw"]
                timestamp_utc = row["timestamp_utc"]
                recebido_em = row["recebido_em"]

                meta = interpretar_topico(topico)

                if not meta:
                    print(f"[WARN] Tópico ignorado: {topico}")
                    last_id = rid
                    continue

                try:
                    inserir_curated(cur, meta, payload, timestamp_utc, recebido_em)
                except Exception as e:
                    print(f"[ERRO] Falha ao inserir curated para id={rid}, topico={topico}: {e}")

                last_id = rid

            conn.commit()
            print(f"[ETL CURATED] Processados até id {last_id}")

    except KeyboardInterrupt:
        print("\n[ETL CURATED] Encerrando...")

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    etl_curated_loop()