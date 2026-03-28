# 🧪 Simulador de Variáveis — simulacao.py

O script **simulacao.py** gera dados sintéticos para testes do pipeline, imitando o comportamento dos instrumentos e sensores industriais utilizados e publicando via MQTT.

---

## 🎯 Objetivo

- Simular variáveis de fermentação, destilação e utilidades
- Publicar em tópicos MQTT compatíveis com o CLP Siemens S7‑1200
- Permitir testes completos e validação do pipeline

---

## ⚙️ Funcionamento

1. Gera valores aleatórios dentro de faixas realistas  
2. Monta payload JSON:
   ```json
   {"valor": 32.5, "qualidade": "GOOD"}

---

## 📦 Dependências

- paho-mqtt
- random
- time

---

## 🧠 Observações

- Útil para testes de carga
- Pode simular falhas e ruídos
- Não é necessário em produção
