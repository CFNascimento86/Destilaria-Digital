# Destilaria-Digital
Transformando variáveis de processo em indicadores estratégicos.

---

## 🚀 Visão Geral

Este projeto implementa uma arquitetura completa de ingestão, tratamento e disponibilização de dados industriais em tempo real. Os dados utilizados neste projeto são provenientes de um **CLP Siemens S7‑1200**, configurado para publicar variáveis de processo via **protocolo MQTT nativo**.  
Essa abordagem elimina a necessidade de gateways OPC ou drivers proprietários, permitindo comunicação leve, rápida e altamente compatível com arquiteturas modernas de IIoT.

As variáveis publicadas incluem:

- Temperaturas de processo  
- Vazões  
- Níveis  
- Pressões  
- Teor alcoólico  
- Consumo energético  
- Indicadores de utilidades  

Esses dados são enviados continuamente para o broker MQTT (Mosquitto), armazenados na camada RAW (PostgreSQL) e processados pelo ETL Curated.

O objetivo atingido foi construir um pipeline industrial robusto, escalável e confiável, capaz de processar dados em tempo real e gerar indicadores estratégicos, capaz de:

- receber dados diretamente de um CLP  
- processar e tratar informações em tempo real  
- consolidar indicadores estratégicos  
- alimentar dashboards e sistemas de supervisão  

Essa arquitetura traz como resultado um pipeline industrial completo, simples de manter e extremamente eficiente.

---

## 🏗️ Arquitetura

O fluxo de dados parte de um **CLP Siemens S7‑1200**, que publica variáveis de processo (temperatura, nível, vazão, pressão, teor alcoòlico.) diretamente em um broker MQTT. A partir daí, o pipeline segue pelas camadas RAW → CURATED → GOLD.

                 +-----------------------------+
                 |  CLP Siemens S7‑1200 (MQTT) |
                 +--------------+--------------+
                                |
                                v
                 +-----------------------------+
                 |   Mosquitto MQTT (Broker)   |
                 +--------------+--------------+
                                |
                                v
                 +-----------------------------+
                 |         RAW Layer           |
                 |   PostgreSQL (raw schema)   |
                 +--------------+--------------+
                                |
                                v
                 +-----------------------------+
                 |     ETL Curated (Python)    |
                 |      Serviço contínuo       |
                 +--------------+--------------+
                                |
                                v
                 +-----------------------------+
                 |        CURATED Layer        |
                 | PostgreSQL (curated schema) |
                 +--------------+--------------+
                                |
                                v
                 +-----------------------------+
                 |         GOLD Layer          |
                 | Materialized Views (KPIs)   |
                 +--------------+--------------+
                                |
                                v
                 +-----------------------------+
                 |     Dashboards / BI         |
                 +-----------------------------+
