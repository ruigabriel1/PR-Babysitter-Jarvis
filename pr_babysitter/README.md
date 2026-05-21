# PR Babysitter - Jarvis 🤖

Este é o Agente Autônomo de Code Review e PR Babysitter construído seguindo o protocolo V.L.A.E.G.S e a Arquitetura em 3 Camadas A.N.T.

## 🚀 Sobre o Projeto
O Jarvis atua interceptando webhooks do GitHub/GitLab, realizando a análise de código usando Linter (Ruff) e um LLM local (Ollama com Phi-3) para gerar comentários de Code Review inline no Pull Request.
Ele implementa o conceito de **Quality Gate Diferencial** (Baseline armazenada em SQLite). O código novo não pode ser pior do que a versão atual na branch principal.

## 🧠 Arquitetura e Decisões Técnicas
- **A.N.T (3 Camadas):**
  - `architecture/`: POPs em markdown definem a regra de negócio da Catraca e Fluxos.
  - `api/main.py`: Camada de Navegação, roteia o payload e toma decisões determinísticas.
  - `tools/`: Camada de Ferramentas, scripts atômicos que executam as lógicas pesadas (Github API, Ollama Client, Linter).
- **LLM Local (Zero Trust):** Por exigência de segurança e privacidade, a OpenAI foi removida. O LLM (Phi-3) roda inteiramente via Docker no serviço `ollama`. Nenhuma linha de código proprietário sai da infraestrutura.
- **SQLite (Baseline):** Utilizado para guardar as métricas oficiais de Code Coverage, Complexidade e Vulns. Um banco relacional simples foi escolhido pela leveza, sendo persistido através de volume Docker.

## ⚙️ Como Executar (First Try)
1. Clone este repositório e renomeie o `.env.example` para `.env`.
2. Preencha o arquivo `.env` com seu `GITHUB_TOKEN` (com permissão de repo/pull requests).
3. Na raiz, rode o comando:
   ```bash
   docker-compose up --build
   ```
4. Acesse o **Dashboard** em: [http://localhost:8000/](http://localhost:8000/)
5. *(Opcional)* Na primeira execução, o serviço do Ollama baixará o modelo `phi3` automaticamente (aguarde o log `pulling manifest`).

## 📚 Pontos Aprendidos e Refatoração (Para Produção)
- **Webhooks & Timeout:** O tempo de reposta inicial (Cold Start) do modelo Phi-3 pode gerar timeout nas entregas de webhook do GitHub (> 10s). Em um ambiente de produção real, usaremos mensageria (ex: Celery/Redis) para colocar o payload na fila, responder o GitHub com HTTP 202 imediatamente e rodar a IA em background.
- **Banco de Dados:** Para milhares de PRs diários, migraríamos a base de Baseline de SQLite para um PostgreSQL isolado na mesma rede Docker.

## 🧪 Caso de Teste Explícito
Veja a simulação passo a passo de reprovação e aprovação da Catraca no arquivo:
👉 **[architecture/caso_de_teste.md](./architecture/caso_de_teste.md)**
