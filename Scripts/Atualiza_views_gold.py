import time
import psycopg2
from datetime import datetime

# Configurações do PostgreSQL
PG_CONFIG = {
    "host": "localhost",     
    "database": "Destilaria",
    "user": "VS_Destilaria",
    "password": "*******",
    "port": 5432,
}

# Lista das materialized views da camada Gold
VIEWS = [
    "gold.mv_fermentacao_horaria",
    "gold.mv_destilacao_horaria",
    "gold.mv_utilidades_horaria",
    "gold.kpi_eficiencia_fermentacao",
    "gold.kpi_eficiencia_destilacao",
    "gold.kpi_consumo_especifico"
]

def atualizar_views():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()

        print(f"\n[{datetime.utcnow()}] Iniciando atualização das materialized views...")

        for view in VIEWS:
            try:
                print(f"Atualizando {view} ...")
                cur.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view};")
                conn.commit()
                print(f"✔ {view} atualizada com sucesso.")
            except Exception as e:
                print(f"❌ Erro ao atualizar {view}: {e}")
                conn.rollback()

        cur.close()
        conn.close()

        print(f"[{datetime.utcnow()}] Atualização concluída.")

    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")

def loop_atualizacao():
    while True:
        atualizar_views()
        print("Aguardando 1 hora para a próxima atualização...\n")
        time.sleep(3600)  # 1 hora

if __name__ == "__main__":
    loop_atualizacao()
