# Bibliotecas ==========================
import json
import psycopg2
import psycopg2.pool
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# =======================================
# CONFIGURAÇÕES DO BROKER MQTT

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "destilaria/#"

# ========================================
# CONFIGURAÇÕES DO POSTGRESQL

PG_HOST = "localhost"
PG_DB = "Destilaria"
PG_USER = "VS_Destilaria"
PG_PASS = "*******"
PG_PORT = 5432

# Pool de conexões =======================

pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    host=PG_HOST,
    database=PG_DB,
    user=PG_USER,
    password=PG_PASS,
    port=PG_PORT
)

# ==========================================
# FUNÇÃO DE INSERÇÃO NO POSTGRESQL

def inserir_no_postgres(topico, payload):
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()

        sql = """
            INSERT INTO raw.medidas_brutas_destilaria
            (timestamp_utc, topico, payload_raw)
            VALUES (%s, %s, %s)
        """

        timestamp_utc = payload.get("timestamp", datetime.now(timezone.utc).isoformat())

        cur.execute(sql, (timestamp_utc, topico, json.dumps(payload)))
        conn.commit()

        cur.close()
        print(f"[OK] Inserido no PostgreSQL → {topico}")

    except Exception as e:
        print("\n[ERRO] Falha ao inserir no PostgreSQL:")
        print(e)
        print("Payload recebido:", payload)
        print("Tópico:", topico)

    finally:
        if conn:
            pool.putconn(conn)

# =================================================
# CALLBACKS MQTT

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT!")
        client.subscribe(MQTT_TOPIC)
        print(f"Assinando tópico: {MQTT_TOPIC}")
    else:
        print(f"Erro ao conectar. Código: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except:
        print(f"[ERRO] Payload inválido no tópico {msg.topic}")
        return

    inserir_no_postgres(msg.topic, payload)

# ====================================================
# LOOP PRINCIPAL

def main():
    print("Iniciando serviço de ingestão MQTT → PostgreSQL...")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# ======================================================

if __name__ == "__main__":
    main()
