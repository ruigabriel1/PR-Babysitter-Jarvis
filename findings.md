# Pesquisas e Descobertas

## Restrições e Escopo (PR Babysitter)
- **Agente de Code Review Autônomo:** Atua no CI/CD interceptando webhooks do GitHub/GitLab.
- **Mecanismo de Baseline (Análise Diferencial):** Métricas da `main` isoladas em banco **SQLite** (volume). PR não pode piorar o estado atual.
- **Quality Gate:** 
  - Regra de Segurança Absoluta (0 vulns).
  - Regra Diferencial (Cobertura de testes do PR >= Cobertura da Baseline).
  - Regra Ponderada (Nota Final >= 80 baseada em Segurança, Complexidade, Boas Práticas, Tratamento de Erros).
- **Entregáveis Obrigatórios:** `README.md`, `docker-compose.yml`, Caso de Teste explícito, `.env` funcional, e **Dashboard de Relatório**.
- **IA e Integração:** Modelo LLM deve rodar **localmente** via **Ollama (Phi-3)**. Uso de OpenAI é **proibido**.
- **Persona:** "Jarvis". Tom de voz objetivo e direto.
