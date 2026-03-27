OBS: obedecendo as diretrizes da LGPD e a confidencialidade do Cliente, os dados desse script serão gerados de forma sintética,
mas sendo fidedignos ao processo.

#Bibliotecas ==========================
import random
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# ============================================================
# CONFIGURAÇÕES DO BROKER MQTT

MQTT_BROKER = "localhost"       # IP ou hostname do broker
MQTT_PORT = 1883                # Porta padrão
MQTT_USER = ""                  # Usuário (se houver)
MQTT_PASS = ""                  # Senha (se houver)
MQTT_QOS = 1                    # QoS recomendado para processo

# ============================================================
# FUNÇÕES AUXILIARES

def gerar_valor(base, variacao, minimo=None, maximo=None):
    valor = base + random.uniform(-variacao, variacao)
    if minimo is not None:
        valor = max(valor, minimo)
    if maximo is not None:
        valor = min(valor, maximo)
    return round(valor, 3)

def timestamp():
    return datetime.now(timezone.utc).isoformat()

# ============================================================
# SIMULADORES POR ÁREA

# ---------------------------
# 1. FERMENTAÇÃO
# ---------------------------
def simular_fermentacao():
    dados = {}

    for Dorna in range(1, 5):
        prefixo = f"Dorna_{Dorna:02d}"
        dados[f"{prefixo}/temperatura_pv"] = gerar_valor(32, 2, 28, 35)
        dados[f"{prefixo}/nivel_pv"] = gerar_valor(70, 10, 0, 100)
        dados[f"{prefixo}/ph_pv"] = gerar_valor(4.5, 0.3, 3.5, 5.5)
        dados[f"{prefixo}/condutividade_pv"] = gerar_valor(1500, 300, 500, 3000)
        dados[f"{prefixo}/densidade_pv"] = gerar_valor(8, 2, 0, 12)

    dados["geral/vazao_mosto"] = gerar_valor(25, 5, 5, 50)
    dados["geral/vazao_ar"] = gerar_valor(100, 30, 10, 200)
    dados["geral/pressao_co2"] = gerar_valor(1.0, 0.2, 0.5, 2.0)

    return dados

# ---------------------------
# 2. DESTILAÇÃO
# ---------------------------
def simular_destilacao():
    dados = {}

    dados["colunaA/temperatura_fundo"] = gerar_valor(85, 5, 70, 110)
    dados["colunaA/temperatura_inferior"] = gerar_valor(85, 5, 70, 110)
    dados["colunaA/temperatura_media"] = gerar_valor(85, 5, 70, 110)
    dados["colunaA/temperatura_superior"] = gerar_valor(85, 5, 70, 110)
    dados["colunaA/temperatura_saida"] = gerar_valor(85, 5, 70, 110)
    
    dados["colunaA/pressao_topo"] = gerar_valor(100, 10, 80, 120)
    dados["colunaA/pressao_fundo"] = gerar_valor(130, 10, 100, 150)

    dados["colunaA/nivel_vinho"] = gerar_valor(60, 20, 0, 100)
    dados["colunaA/nivel_flegma"] = gerar_valor(50, 20, 0, 100)
    dados["colunaA/nivel_etanol"] = gerar_valor(40, 20, 0, 100)

    dados["colunaA/vazao_vapor"] = gerar_valor(12, 3, 1, 20)
    dados["colunaA/vazao_refluxo"] = gerar_valor(3, 1, 0.5, 5)

    dados["colunaA/teor_alcool"] = gerar_valor(96, 2, 92, 99.5)

    dados["colunaB/temperatura_fundo"] = gerar_valor(85, 5, 70, 110)
    dados["colunaB/temperatura_inferior"] = gerar_valor(85, 5, 70, 110)
    dados["colunaB/temperatura_media"] = gerar_valor(85, 5, 70, 110)
    dados["colunaB/temperatura_superior"] = gerar_valor(85, 5, 70, 110)
    dados["colunaB/temperatura_saida"] = gerar_valor(85, 5, 70, 110)
    
    dados["colunaB/pressao_topo"] = gerar_valor(100, 10, 80, 120)
    dados["colunaB/pressao_fundo"] = gerar_valor(130, 10, 100, 150)

    dados["colunaB/nivel_fundo_coluna"] = gerar_valor(60, 20, 0, 100)
    dados["colunaB/nivel_tambor_refluxo"] = gerar_valor(50, 20, 0, 100)
    
    dados["colunaB/vazao_alcool"] = gerar_valor(3, 1, 0.5, 5)
    dados["colunaB/vazao_vapor"] = gerar_valor(12, 3, 1, 20)
    dados["colunaB/vazao_refluxo"] = gerar_valor(3, 1, 0.5, 5)
    dados["colunaB/vazao_destilado"] = gerar_valor(3, 1, 0.5, 5)

    dados["colunaB/teor_alcool"] = gerar_valor(96, 2, 92, 99.5)

    return dados

# ---------------------------
# 3. UTILIDADES
# ---------------------------
def simular_utilidades():
    dados = {}

    dados["vapor/pressao"] = gerar_valor(8, 2, 4, 12)
    dados["agua/temperatura_entrada"] = gerar_valor(28, 3, 25, 35)
    dados["agua/temperatura_saida"] = gerar_valor(34, 3, 30, 40)
    dados["agua/vazao_resfriamento"] = gerar_valor(250, 50, 50, 500)
    dados["agua/nivel_tq.fria"] = gerar_valor(70, 20, 0, 100)
    dados["agua/nivel_tq.quente"] = gerar_valor(50, 20, 0, 100)
    dados["energia/consumo_eletrico"] = gerar_valor(15000, 2000, 0, None)

    return dados

# ============================================================
# PUBLICAÇÃO MQTT

def publicar_variavel(client, topico, valor):
    payload = {
        "timestamp": timestamp(),
        "valor": valor,
        "unidade": "",
        "qualidade": "GOOD"
    }

    client.publish(topico, json.dumps(payload), qos=MQTT_QOS)
    print(f"[MQTT] {topico} → {payload}")

# ============================================================
# LOOP PRINCIPAL

def main():
    print("Conectando ao broker MQTT...")

    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    print("Simulação iniciada. Publicando dados...\n")

    while True:
        # Fermentação
        fermentacao = simular_fermentacao()
        for var, valor in fermentacao.items():
            publicar_variavel(client, f"destilaria/fermentacao/{var}", valor)

        # Destilação
        destilacao = simular_destilacao()
        for var, valor in destilacao.items():
            publicar_variavel(client, f"destilaria/destilacao/{var}", valor)

        # Utilidades
        utilidades = simular_utilidades()
        for var, valor in utilidades.items():
            publicar_variavel(client, f"destilaria/utilidades/{var}", valor)

        time.sleep(60)  # intervalo entre ciclos


if __name__ == "__main__":
    main()
