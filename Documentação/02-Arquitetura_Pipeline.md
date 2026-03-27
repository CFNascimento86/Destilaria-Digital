📘 02 — Arquitetura do Pipeline de Dados Industrial
Este documento descreve a arquitetura completa do pipeline de dados do projeto Destilaria Digital, detalhando cada camada, seus componentes, responsabilidades e fluxos de comunicação.
A solução foi projetada para integrar dados industriais provenientes de um CLP Siemens S7‑1200 via MQTT, processá‑los em tempo real e disponibilizá‑los como indicadores estratégicos.

🏗️ 1. Visão Geral da Arquitetura
O pipeline segue o modelo clássico de três camadas:
- RAW → dados brutos recebidos diretamente do CLP
- CURATED → dados tratados, normalizados e enriquecidos
- GOLD → indicadores, KPIs e agregações para consumo analítico
A comunicação entre os componentes é feita via MQTT e PostgreSQL, com serviços independentes.

🔌 2. Fluxo de Dados (Visão Macro)
CLP Siemens S7‑1200 (MQTT)
            |
            v
Mosquitto MQTT Broker
            |
            v
RAW Layer (PostgreSQL)
            |
            v
ETL (Python)
            |
            v
CURATED Layer (PostgreSQL)
            |
            v
Atualizador GOLD (Python)
            |
            v
GOLD Layer (Materialized Views)
            |
            v
Dashboards / BI / Supervisão



🧩 3. Componentes da Arquitetura
3.1 CLP Siemens S7‑1200 (MQTT nativo)
O CLP atua como cliente MQTT, publicando variáveis de processo em tópicos estruturados:
destilaria/<area>/<equipamento>/<variavel>


Exemplos:
- destilaria/fermentacao/Dorna_01/temperatura_pv
- destilaria/destilacao/colunaA/pressao_topo
- destilaria/utilidades/agua/temperatura_entrada
O payload é enviado em JSON:
{
  "valor": 32.5,
  "qualidade": "GOOD"
}



3.2 Mosquitto MQTT Broker
Responsável por:
- receber mensagens do CLP
- disponibilizar para consumidores (ETL RAW → CURATED)
- garantir entrega leve e eficiente
Configuração típica:
Porta: 1883
QoS: 0 ou 1
Retain: false



3.3 RAW Layer (PostgreSQL)
A camada RAW armazena dados brutos, sem transformação.
Tabela principal: raw.medidas_brutas_destilaria


Campos:
- id
- timestamp_utc
- topico
- payload_raw (JSONB)
- recebido_em
Essa camada garante:
- rastreabilidade
- auditoria
- reprocessamento
- histórico completo

3.4 ETL Curated (Python)
Serviço contínuo que:
- lê novos registros da RAW
- interpreta o tópico MQTT
- identifica área, equipamento e variável
- normaliza unidades
- insere na camada CURATED
Características:
- roda em loop infinito
- reconecta automaticamente ao banco
- tolerante a falhas
- leve e eficiente

3.5 CURATED Layer (PostgreSQL)
Armazena dados tratados e estruturados.
Tabelas:
- curated.fermentacao
- curated.destilacao
- curated.utilidades
Cada registro contém:
- equipamento
- variavel_base
- variavel_tipo
- valor
- unidade
- qualidade
- data/hora UTC
- data/hora de recebimento
Essa camada é otimizada para:
- consultas rápidas
- consistência
- integridade dos dados

3.6 Atualizador GOLD (Python)
Script que roda a cada hora e executa:
REFRESH MATERIALIZED VIEW CONCURRENTLY <view>


Atualiza:
- agregações horárias
- KPIs
- indicadores de eficiência
- consumo específico
- métricas de processo

3.7 GOLD Layer (Materialized Views)
Camada final, pronta para consumo analítico.
Exemplos:
- gold.mv_fermentacao_horaria
- gold.mv_destilacao_horaria
- gold.kpi_eficiencia_fermentacao
- gold.kpi_consumo_especifico
Benefícios:
- consultas extremamente rápidas
- pré‑agregação
- isolamento da lógica de negócio
- estabilidade para dashboards


🔄 5. Fluxo Detalhado (Passo a Passo)
- CLP S7‑1200 publica variáveis via MQTT
- Mosquitto recebe e distribui
- Um serviço de ingestão grava na RAW
- O ETL lê novos registros
- Interpreta o tópico e normaliza dados
- Insere na CURATED
- A cada hora, o Atualizador GOLD atualiza as materialized views
- Dashboards consomem diretamente da GOLD

🧠 6. Princípios de Design da Arquitetura
- Simplicidade — fácil de entender, manter e evoluir
- Baixo custo — tecnologias open‑source e leves
- Escalabilidade horizontal — cada serviço é independente
- Resiliência — ETL tolerante a falhas
- TO/TI Integration — CLP → MQTT → Banco → BI
- Industrial‑grade — inspirado em arquiteturas reais de chão de fábrica

🏁 7. Conclusão
A arquitetura do pipeline da Destilaria Digital demonstra como integrar dados industriais reais a uma plataforma moderna de dados, utilizando tecnologias acessíveis e práticas recomendadas da Indústria 4.0.
Ela serve como base sólida para:
- dashboards
- análises avançadas
- machine learning
- otimização de processo
- digital twins
