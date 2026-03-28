# 🥇 Atualizador da Camada GOLD

O script **atualiza_views_gold.py** é responsável por atualizar periodicamente todas as materialized views da camada GOLD.

---

## 🎯 Objetivo

- Executar:
- Refresh Materialized View Concurrently
- Garantir que KPIs e agregações estejam sempre atualizados
- Minimizar impacto em dashboards e consultas

---

## ⚙️ Funcionamento

1. Conecta ao PostgreSQL  
2. Atualiza cada view GOLD em sequência  
3. Aguarda 1 hora  
4. Repete indefinidamente  

---

## 📦 Dependências

- psycopg2
- PostgreSQL

---

## 📝 Logs

- início da atualização
- views atualizadas
- erros de refresh
- timestamp da próxima execução

---

## 🧠 Observações

- Usa CONCURRENTLY para não bloquear leitura
- Pode ser executado em paralelo com dashboards
