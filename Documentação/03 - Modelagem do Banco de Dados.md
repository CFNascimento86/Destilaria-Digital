# 📘 03 — Modelagem do Banco de Dados

Este documento descreve a modelagem completa do banco de dados utilizado no projeto Destilaria Digital, incluindo as camadas RAW, CURATED e GOLD, bem como suas relações, objetivos e padrões de design.
O banco foi projetado para suportar ingestão contínua de dados industriais provenientes de um CLP Siemens S7‑1200 via MQTT, garantindo rastreabilidade, consistência e performance analítica.

## 🧱 1. Visão Geral da Modelagem

O banco segue uma arquitetura em camadas:
RAW → CURATED → GOLD

Cada camada possui objetivos distintos:
 
![arquitetura_camadas](https://github.com/user-attachments/assets/2822c0ea-586f-415e-b62f-10845348d163)


## 🟥 2. Esquema RAW

A camada RAW armazena exatamente o que chega do MQTT, sem qualquer transformação.
Tabela: raw.medidas_brutas_destilaria
```
CREATE TABLE raw.medidas_brutas_destilaria (
    id SERIAL PRIMARY KEY,
    timestamp_utc TIMESTAMP NOT NULL,
    topico TEXT NOT NULL,
    payload_raw JSONB NOT NULL,
    recebido_em TIMESTAMP NOT NULL DEFAULT NOW()
);
```
Descrição dos campos

![descricao_campos](https://github.com/user-attachments/assets/ea32c8dc-0c80-4bf2-b6e0-9c4f7b3b4703)


Exemplo de registro
```
{
  "id": 102394,
  "timestamp_utc": "2026-03-26T23:15:00Z",
  "topico": "destilaria/fermentacao/Dorna_01/temperatura_pv",
  "payload_raw": {"valor": 32.5, "qualidade": "GOOD"},
  "recebido_em": "2026-03-26T23:15:00.512Z"
}
```

Objetivos da camada RAW
- Garantir rastreabilidade total
- Permitir reprocessamento
- Registrar histórico bruto
- Servir como fonte única de verdade (Single Source of Truth)

## 🟦 3. Esquema CURATED

A camada CURATED contém dados tratados, normalizados e enriquecidos.
Cada área do processo possui sua própria tabela.

3.1 - Tabela curated.fermentacao
```
CREATE TABLE curated.fermentacao (
    id SERIAL PRIMARY KEY,
    equipamento TEXT NOT NULL,
    variavel_base TEXT NOT NULL,
    variavel_tipo TEXT,
    valor NUMERIC,
    unidade TEXT,
    qualidade TEXT,
    data_utc DATE,
    hora_utc TIME,
    data_recebido DATE,
    hora_recebido TIME
);
```

3.2 - Tabela curated.destilacao

Mesma estrutura da fermentação, porém separada por área:
```
CREATE TABLE curated.destilacao (
    id SERIAL PRIMARY KEY,
    equipamento TEXT NOT NULL,
    variavel_base TEXT NOT NULL,
    variavel_tipo TEXT,
    valor NUMERIC,
    unidade TEXT,
    qualidade TEXT,
    data_utc DATE,
    hora_utc TIME,
    data_recebido DATE,
    hora_recebido TIME
);
```

3.3 - Tabela curated.utilidades
```
CREATE TABLE curated.utilidades (
    id SERIAL PRIMARY KEY,
    equipamento TEXT NOT NULL,
    variavel_base TEXT NOT NULL,
    variavel_tipo TEXT,
    valor NUMERIC,
    unidade TEXT,
    qualidade TEXT,
    data_utc DATE,
    hora_utc TIME,
    data_recebido DATE,
    hora_recebido TIME
);
```

3.4 - Objetivos da camada CURATED

- Normalizar nomes de variáveis
- Padronizar unidades
- Separar áreas do processo
- Facilitar consultas rápidas
- Garantir integridade e consistência

## 🟩 4. Esquema GOLD

A camada GOLD contém materialized views com:
- agregações horárias
- KPIs
- indicadores de eficiência
- métricas de processo
- consumo específico
  
Essas views são atualizadas pelo script:
atualiza_gold.py


4.1 - Exemplo: gold.mv_fermentacao_horaria
```
CREATE MATERIALIZED VIEW gold.mv_fermentacao_horaria AS
SELECT
    equipamento,
    variavel_base,
    date_trunc('hour', data_utc + hora_utc) AS hora,
    AVG(valor) AS valor_medio,
    MIN(valor) AS valor_min,
    MAX(valor) AS valor_max,
    COUNT(*) AS registros
FROM curated.fermentacao
GROUP BY equipamento, variavel_base, hora;
```

4.2 - Exemplo: gold.kpi_eficiencia_destilacao
```
CREATE MATERIALIZED VIEW gold.kpi_eficiencia_destilacao AS
SELECT
    date_trunc('hour', data_utc + hora_utc) AS hora,
    AVG(teor_alcool) AS teor_medio,
    AVG(vazao_destilado) AS vazao_media,
    AVG(pressao_topo) AS pressao_media
FROM curated.destilacao
GROUP BY hora;
```

4.3 - Objetivos da camada GOLD

- Alta performance para dashboards
- Pré‑agregação de dados
- Redução de carga no banco
- KPIs consistentes e auditáveis
- Base para análises avançadas


## 🔗 5. Relacionamento entre as camadas

RAW.id → CURATED (processado sequencialmente)

CURATED → GOLD (via materialized views)

Não há chaves estrangeiras entre camadas, por design:
- RAW é imutável
- CURATED é derivada
- GOLD é agregada
  
Esse desacoplamento aumenta:
- resiliência
- performance
- flexibilidade
- capacidade de reprocessamento

## 🧠 6. Princípios de Design da Modelagem

- Simplicidade: tabelas claras e diretas
- Escalabilidade: particionamento futuro possível
- Performance: GOLD otimizada para leitura
- Rastreabilidade: RAW preserva tudo
- TO/TI Integration: estrutura compreensível para ambos os mundos
- Industrial-grade: inspirado em arquiteturas reais de plantas químicas e alimentícias

## 🏁 7. Conclusão

A modelagem do banco de dados da Destilaria Digital foi projetada para suportar ingestão contínua de dados industriais, garantindo confiabilidade, rastreabilidade e performance analítica.
Ela serve como base sólida para:
- dashboards
- análises avançadas
- machine learning
- otimização de processo
- digital twins
