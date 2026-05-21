# Gemini - Constituição do Projeto (PR Babysitter)

## 1. Data Schemas (Esquemas de Dados)
- **Payload de Entrada (Webhook GitHub):** JSON contendo `action`, `pull_request.number`, `repository.full_name`, e URL do diff.
- **Payload de Saída (Review GitHub):** Chamada POST para criar Review Comments (`body`, `commit_id`, `path`, `line`, `event="REQUEST_CHANGES"` ou `"APPROVE"`).
- **Payload de Saída (Dashboard):** Relatório gerado em HTML para visualização das métricas da Baseline x PR atual.

## 2. Regras Comportamentais
- **Persona:** Jarvis. Tom de voz objetivo e direto.
- **Sem IA Externa:** Proibido uso de OpenAI. O LLM deve rodar localmente no Docker usando Ollama (modelo Phi-3).
- **Fonte da Verdade:** Banco SQLite armazenado em volume isolado no Docker.

## 3. Invariantes Arquiteturais
- **Arquitetura A.N.T. (3 Camadas):**
  - **Camada 1 (`architecture/`):** POPs (Procedimentos Operacionais Padrão) em Markdown.
  - **Camada 2 (Navegação):** Decisão LLM determinística baseada nos POPs.
  - **Camada 3 (`tools/`):** Scripts Python atômicos, testáveis e determinísticos.
- **Persistência Temporária:** Todos os artefatos intermediários usam `.tmp/`.
- **Armazenamento Isolado (Baseline):** As métricas oficiais da branch principal são salvas em um banco/volume Docker não editável via PR.
- **Proteção de Segredos (Zero Trust):** Nenhum token ou chave `hardcoded`. Exclusivamente gerenciados no `.env`.
