# 📡 Configuração do Protocolo MQTT no CLP Siemens S7‑1200

Este documento descreve, de forma técnica e objetiva, como configurar um **CLP Siemens S7‑1200** para publicar variáveis de processo utilizando o **protocolo MQTT nativo**, integrando diretamente com o broker Mosquitto utilizado no projeto *Destilaria Digital*.

---

## 🧩 1. Requisitos

### **Hardware**
- Siemens S7‑1200 (CPU 1212C, 1214C, 1215C ou superior)
- Firmware V4.4 ou superior (necessário para suporte MQTT nativo)
- Módulo de comunicação Ethernet integrado

### **Software**
- TIA Portal V17 ou superior
- Biblioteca MQTT da Siemens (nativa a partir da V17)
- Acesso ao broker MQTT (Mosquitto)

---

## 🔌 2. Arquitetura de Comunicação

O CLP atua como **cliente MQTT**, publicando variáveis de processo em tópicos estruturados:

Exemplos:

- `destilaria/fermentacao/Dorna_01/temperatura_pv`
- `destilaria/destilacao/colunaA/pressao_topo`
- `destilaria/utilidades/agua/temperatura_entrada`

O broker MQTT utilizado é o **Mosquitto**:
Host: 192.168.0.10 (exemplo) Porta: 1883 QoS: 0 ou 1

---

## ⚙️ 3. Habilitando MQTT no TIA Portal

1. Abra o projeto no **TIA Portal**  
2. No painel de navegação, selecione:  
   **Device configuration → Properties → MQTT**  
3. Ative a opção:  
   **Enable MQTT communication**  
4. Configure o cliente MQTT:
   - **Client ID:** `S7-1200-Destilaria`
   - **Keep Alive:** 60 s
   - **Clean Session:** habilitado
   - **Reconnect:** automático

---

## 🌐 4. Configurando o Broker MQTT

No TIA Portal:

1. Vá em **Connections → MQTT Broker**  
2. Adicione um novo broker:
   - **Broker Address:** IP do Mosquitto  
   - **Port:** 1883  
   - **Protocol:** MQTT v3.1.1  
3. Se necessário, configure autenticação:
   - **Username:** opcional  
   - **Password:** opcional  

> OBS: Para o projeto Destilaria Digital, utilizamos broker sem autenticação para simplificar o ambiente de desenvolvimento.

---

## 📝 5. Criando os Tópicos MQTT

Cada variável do processo foi publicada em um tópico específico.

Exemplo de estrutura recomendada:

| Área          | Equipamento  | Variável             | Tópico MQTT |
|---------------|--------------|-----------------------|-------------|
| Fermentação   | Dorna_01     | temperatura_pv        | `destilaria/fermentacao/Dorna_01/temperatura_pv` |
| Destilação    | colunaA      | pressao_topo          | `destilaria/destilacao/colunaA/pressao_topo` |
| Utilidades    | agua         | temperatura_entrada   | `destilaria/utilidades/agua/temperatura_entrada` |

---

## 🧱 6. Blocos de Função MQTT no S7‑1200

O TIA Portal fornece três blocos principais:

### **1. MQTT_Connect**
Estabelece conexão com o broker.

Parâmetros importantes:
- `BrokerAddr`
- `BrokerPort`
- `ClientID`
- `Connect`

### **2. MQTT_Publish**
Publica mensagens em um tópico.

Parâmetros:
- `Topic`
- `Payload`
- `QoS`
- `Retain`
- `Publish`

### **3. MQTT_Disconnect**
Finaliza a conexão.

---

## 🔄 7. Exemplo de Publicação de Variáveis

### **Bloco MQTT_Publish configurado:**

- **Topic:**  
  `"destilaria/fermentacao/Dorna_01/temperatura_pv"`
- **Payload:**  
  JSON contendo valor e qualidade:
```
{
  "valor": 32.5,
  "qualidade": "GOOD"
}
```
### **Lógica SCL (exemplo):**
```
IF PublishTrigger THEN
    MQTT_Publish(
        Topic := 'destilaria/fermentacao/Dorna_01/temperatura_pv',
        Payload := TempFermentacaoJSON,
        QoS := 0,
        Retain := FALSE,
        Publish := TRUE
    );
END_IF;
```
### **Testando a comunicação no PC:**

mosquitto_sub -h <IP_DO_BROKER> -t "destilaria/#" -v

---

 ## 🏁 8. Conclusão
 
Com o MQTT nativo do S7‑1200, é possível integrar o CLP diretamente a arquiteturas modernas de dados industriais, eliminando gateways OPC e reduzindo custos.
Essa configuração é a base da ingestão de dados do projeto Destilaria Digital.
