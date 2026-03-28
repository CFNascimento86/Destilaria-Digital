# 🧩 ETL Curated — Destilaria Digital

O script **etl_curated.py** é responsável por transformar dados da camada RAW em dados tratados na camada CURATED.  
Ele roda continuamente, monitorando novos registros e aplicando regras de normalização, enriquecimento e padronização.

---

## 🎯 Objetivo

- Ler dados brutos da tabela `raw.medidas_brutas_destilaria`
- Interpretar tópicos MQTT publicados pelo CLP Siemens S7‑1200
- Normalizar variáveis, unidades e estrutura
- Inserir registros tratados nas tabelas:
  - `curated.fermentacao`
  - `curated.destilacao`
  - `curated.utilidades`

---

## ⚙️ Funcionamento

O script:

1. Conecta ao PostgreSQL  
2. Identifica o último `id` processado  
3. Busca novos registros na RAW  
4. Interpreta o tópico MQTT  
5. Normaliza:
   - variável base  
   - tipo da variável  
   - unidade  
   - timestamps  
6. Insere na tabela CURATED correspondente  
7. Repete continuamente

---

## 📝 Logs

O script imprime:
- início do processamento
- último ID processado
- avisos de tópicos desconhecidos
- erros de inserção

---

## 🧠 Observações

- O ETL é tolerante a falhas
- Reconecta automaticamente ao banco
- Pode ser escalado horizontalmente (sharding por área)

---

# 📡 Ingestão RAW — ingestao_destilaria.py

O script **ingestao_destilaria.py** é responsável por receber mensagens MQTT enviadas pelo CLP Siemens S7‑1200 e gravá‑las na camada RAW do banco de dados.

---

## 🎯 Objetivo

- Assinar tópicos MQTT da destilaria
- Receber payloads JSON enviados pelo CLP
- Registrar dados brutos na tabela:
  - `raw.medidas_brutas_destilaria`

---

## ⚙️ Funcionamento

1. Conecta ao broker Mosquitto  
2. Assina os tópicos:
3. Para cada mensagem recebida:
- lê o tópico  
- lê o payload JSON  
- registra no banco com timestamp de recebimento  

---

## 📦 Dependências

- paho-mqtt
- psycopg2
- PostgreSQL
- Mosquitto

---

## 📝 Logs

- mensagens recebidas
- erros de conexão
- falhas de inserção

---

## 🧠 Observações

- É o ponto de entrada do pipeline
- Mantém rastreabilidade total dos dados
