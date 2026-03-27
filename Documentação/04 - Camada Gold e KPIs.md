# 📘 04 — Camada GOLD e KPIs

A camada GOLD representa o nível mais alto de maturidade dentro do pipeline de dados da Destilaria Digital.
Ela é responsável por consolidar informações tratadas, gerar indicadores estratégicos e entregar dados prontos para consumo por dashboards, sistemas de supervisão, relatórios e análises avançadas.
A GOLD é construída sobre Materialized Views do PostgreSQL, garantindo alta performance, consistência e isolamento da lógica de negócio.

## 🥇 1. Objetivos da Camada GOLD

A camada GOLD foi projetada para:
- Fornecer KPIs confiáveis para tomada de decisão
- Reduzir carga computacional sobre as camadas RAW e CURATED
- Padronizar cálculos e métricas
- Garantir performance analítica
- Servir como base para dashboards industriais
- Isolar a lógica de negócio em um único ponto
  
Ela é atualizada periodicamente pelo script: atualiza_gold.py

que executa: REFRESH MATERIALIZED VIEW CONCURRENTLY <view>


## 🧱 2. Estrutura da Camada GOLD

A GOLD é composta por dois tipos principais de objetos:

### 1. Materialized Views de Agregação
- agregações horárias
- médias, mínimos, máximos
- contagem de registros
- consolidação por equipamento e variável

### 2. Materialized Views de KPIs
- eficiência de fermentação
- eficiência de destilação
- consumo específico
- balanços de massa e energia
- indicadores de estabilidade de processo

## 🟦 3. Materialized Views de Agregação

Essas views consolidam dados da camada CURATED em janelas horárias, reduzindo drasticamente o volume de dados para dashboards.

### 3.1 - Fermentação — Agregação Horária
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
Indicadores gerados
- temperatura média por Dorna
- pH médio
- densidade média
- vazão de mosto
- pressão de CO₂

### 3.2 - Destilação — Agregação Horária
```
CREATE MATERIALIZED VIEW gold.mv_destilacao_horaria AS
SELECT
    equipamento,
    variavel_base,
    date_trunc('hour', data_utc + hora_utc) AS hora,
    AVG(valor) AS valor_medio,
    MIN(valor) AS valor_min,
    MAX(valor) AS valor_max,
    COUNT(*) AS registros
FROM curated.destilacao
GROUP BY equipamento, variavel_base, hora;
```
Indicadores gerados
- temperatura de fundo / topo
- pressão de topo
- nível de vinho / flegma
- vazão de vapor
- vazão de destilado
- teor alcoólico médio

### 3.3 - Utilidades — Agregação Horária
```
CREATE MATERIALIZED VIEW gold.mv_utilidades_horaria AS
SELECT
    equipamento,
    variavel_base,
    date_trunc('hour', data_utc + hora_utc) AS hora,
    AVG(valor) AS valor_medio,
    MIN(valor) AS valor_min,
    MAX(valor) AS valor_max,
    COUNT(*) AS registros
FROM curated.utilidades
GROUP BY equipamento, variavel_base, hora;
```
Indicadores gerados
- temperatura de entrada/saída
- pressão de vapor
- vazão de resfriamento
- consumo elétrico

## 🟩 4. KPIs Estratégicos

A seguir estão os principais KPIs implementados na camada GOLD.

### 4.1 - Eficiência da Fermentação
Indicador baseado em:
- densidade inicial
- densidade final
- tempo de fermentação
- temperatura média
- estabilidade do processo
```
CREATE MATERIALIZED VIEW gold.kpi_eficiencia_fermentacao AS
SELECT
    hora,
    AVG(densidade_final - densidade_inicial) AS reducao_brix,
    AVG(temperatura_media) AS temperatura_media,
    COUNT(*) AS ciclos
FROM gold.mv_fermentacao_horaria
GROUP BY hora;
```
### 4.2 - Eficiência da Destilação
Baseado em:
- teor alcoólico do destilado
- vazão de vapor
- vazão de refluxo
- pressão de topo
- estabilidade térmica
```
CREATE MATERIALIZED VIEW gold.kpi_eficiencia_destilacao AS
SELECT
    hora,
    AVG(teor_alcool) AS teor_medio,
    AVG(vazao_destilado) AS vazao_media,
    AVG(pressao_topo) AS pressao_media
FROM gold.mv_destilacao_horaria
GROUP BY hora;
```

### 4.3 - Consumo Específico

Energia consumida por litro de destilado produzido.
```
CREATE MATERIALIZED VIEW gold.kpi_consumo_especifico AS
SELECT
    h.hora,
    SUM(u.valor_medio) AS energia_kwh,
    SUM(d.valor_medio) AS litros_destilado,
    SUM(u.valor_medio) / NULLIF(SUM(d.valor_medio), 0) AS kwh_por_litro
FROM gold.mv_utilidades_horaria u
JOIN gold.mv_destilacao_horaria d
    ON u.hora = d.hora
WHERE u.variavel_base = 'consumo_eletrico'
  AND d.variavel_base = 'vazao_destilado'
GROUP BY h.hora;
```

## 🧠 5. Por que Materialized Views?

Materialized Views foram escolhidas porque:
- são extremamente rápidas para leitura
- reduzem carga sobre CURATED
- permitem cálculos complexos sem penalizar dashboards
- podem ser atualizadas incrementalmente
- são ideais para dados industriais de alta frequência

## 🔄 6. Atualização das Views

O script atualiza_gold.py executa: 
cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY gold.mv_fermentacao_horaria;")


Vantagens do modo CONCURRENTLY:
- não bloqueia leitura
- dashboards continuam funcionando
- atualização suave e contínua

## 📊 7. Consumo da Camada GOLD

A GOLD é consumida por:
- Grafana
- Power BI
- Tableau
- Sistemas de supervisão
- Aplicações internas
- APIs industriais

Como as views já estão pré‑agregadas, a performance é excelente mesmo com:
- dashboards em tempo real
- múltiplos usuários
- consultas simultâneas

## 🏁 8. Conclusão

A camada GOLD é o coração analítico da Destilaria Digital.
Ela transforma dados industriais brutos em informação estratégica, pronta para:
- otimização de processo
- redução de custos
- aumento de eficiência
- tomada de decisão baseada em dados
- análises avançadas e machine learning
  
Com essa camada, o pipeline atinge maturidade industrial e se torna uma solução completa de Indústria 4.0.
