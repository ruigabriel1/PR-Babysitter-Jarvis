# PR Babysitter (Jarvis) 🤖🛡️

O **PR Babysitter** é um agente autônomo de Inteligência Artificial desenhado para atuar no ecossistema de Integração Contínua (CI/CD) de repositórios GitHub. Operando sob a persona de "Jarvis" (um Tech Lead rigoroso), ele substitui o microgerenciamento humano em revisões de código.

Através de uma **Catraca (Quality Gate)** baseada em regras matemáticas rígidas, ele avalia se o novo código degrada a saúde do projeto. Se houver falha, ele trava a esteira e utiliza uma **LLM Local (Phi-3 via Ollama)** para gerar *code reviews* construtivos ("babysit") e sugerir correções *inline* diretamente no Pull Request.

---

## 🏗️ Arquitetura A.N.T (3 Camadas)

Este projeto foi construído seguindo o protocolo de alta manutenibilidade **A.N.T (Arquitetura, Navegação e Ferramentas)**:

1. **Camada 1 (Arquitetura / POPs):** Todas as regras de negócio (Quality Gate) e a árvore de decisões do agente estão documentadas na pasta `architecture/`. A IA não tem permissão para inventar regras, apenas segui-las determinística e matematicamente.
2. **Camada 2 (Navegação):** O servidor web (FastAPI em `api/main.py`) atua como o maestro, recebendo webhooks do GitHub e delegando as execuções para o processamento assíncrono (evitando timeouts).
3. **Camada 3 (Ferramentas Atômicas):** Scripts localizados em `tools/`. Módulos estritos e isolados para bater na API do GitHub, avaliar as notas da Catraca, consultar/escrever no SQLite e realizar chamadas para a LLM.

### Por que SQLite para a Baseline?
A fonte da verdade da nossa régua ("Baseline") não pode ser manipulada no meio de um PR. Por isso, as métricas oficiais da branch `master` ficam presas em um **banco SQLite local isolado** (em `.tmp/baseline.db`). O agente atualiza esse banco **apenas** quando um PR é aprovado e passa pelo Merge oficial.

---

## 🚧 Dificuldades e Desafios (Lições Aprendidas)

Durante o desenvolvimento deste agente autônomo, validamos conceitos complexos do fluxo GitOps. Algumas das maiores pedreiras enfrentadas e domadas foram:

1. **Virtualização Local (Docker Bloqueado):** O desafio inicial previa o uso nativo do Docker para o container do Ollama. Devido a limitações de hardware (virtualização desabilitada na BIOS), tivemos que adaptar o ecossistema para rodar o FastAPI puramente no Python do Windows, injetando temporariamente um Mock da IA para não travar a prova de conceito.
2. **A Barreira do GitHub Token (401 e 403):** Entender a taxonomia dos tokens do GitHub foi essencial. Primeiramente lidamos com `401 Bad Credentials` pela falta de injeção da variável `.env` fora do Docker. Depois o `403 Forbidden` devido ao *scope* do token, provando que o agente exige poder total de leitura/escrita no repositório (Escopo `repo`).
3. **O Limite de Auto-Revisão do GitHub (Erro 422):** A Catraca funcionou perfeitamente para "Aprovar" (APPROVE) ou "Solicitar Mudanças" (REQUEST_CHANGES), mas a API do GitHub nos retornou um `422 Unprocessable Entity` com a mensagem *"Review Can not approve your own pull request"*. Para fins de teste (onde o robô usa o mesmo token do dono do código), mitigamos isso convertendo os eventos finais para `COMMENT` acompanhados de uma formatação rica em Markdown.

---

## 🚀 Plano de Refatoração (Para subir a Produção)

Apesar de funcional, esta arquitetura mockada deve receber os seguintes upgrades antes de ser conectada em uma esteira corporativa real:

- **Substituir Mocks por Análise Real Estática:** Conectar o script à ferramentas reais de análise. Fazer o download do diff do PR e rodar `pytest --cov`, `pylint` ou `SonarScanner` dinamicamente dentro de containers limpos efêmeros, injetando os valores reais na Catraca.
- **Banco de Dados Persistente na Nuvem:** Mudar o SQLite para um banco PostgreSQL gerenciado (RDS/Supabase), permitindo que múltiplos repositórios utilizem o agente sem conflitos de disco efêmero do Docker.
- **Isolamento de Webhooks Secretos:** Adicionar verificação de Assinatura HMAC nas requisições do GitHub para impedir ataques no endpoint público `/webhook`.
- **Deploy Serverless/Kubernetes:** Mover a API FastAPI para o Google Cloud Run ou AWS ECS, subindo o container do Ollama separadamente em uma máquina com GPU otimizada (como EC2 g4dn) para que a resposta da IA seja menor que 2 segundos.

---

## 🛠️ Tutorial de Execução (Como Usar)

O projeto está configurado para operar de forma autossuficiente via `docker-compose`, rodando o servidor Python e baixando o modelo Phi-3 simultaneamente.

### Pré-requisitos:
- Docker Desktop instalado e virtualização ativa.
- Um **Personal Access Token (Classic)** do GitHub com a caixinha `repo` marcada.
- Ngrok instalado na máquina.

### Passo a Passo

1. **Configure o `.env`**
   Na raiz deste projeto, crie ou altere o arquivo `.env` incluindo seu token:
   ```env
   GITHUB_TOKEN=ghp_SEUTOKENAQUI...
   ```

2. **Inicie o Container Central**
   No terminal, rode:
   ```bash
   docker-compose up --build
   ```
   *Nota: No primeiro uso, o Ollama fará o download do modelo Phi-3 (~2GB), o que pode levar alguns minutos. Aguarde a inicialização completa da porta 8000.*

3. **Crie o Túnel Webhook**
   Em um segundo terminal, abra a sua porta para a nuvem:
   ```bash
   ngrok http 8000
   ```
   Copie a URL "Forwarding" verdinha gerada (Ex: `https://abcd.ngrok-free.app`).

4. **Cadastre no GitHub**
   - Acesse o repositório > **Settings** > **Webhooks** > **Add Webhook**.
   - **Payload URL**: Cole seu link do Ngrok seguido de `/webhook`.
   - **Content type**: `application/json`.
   - Marque apenas a caixa **Pull requests**. Salve.

### 🧪 Caso de Teste Explícito (Forçando a Catraca)

1. Vá no terminal do seu projeto e crie uma branch isolada:
   ```bash
   git checkout -b branch-teste-catraca
   ```
2. Abra o arquivo `api/main.py`, insira espaços ou comentários extras, e salve.
3. Commit e Push:
   ```bash
   git add .
   git commit -m "chore: testando qualidade"
   git push -u origin branch-teste-catraca
   ```
4. Abra o site do GitHub e clique em **"Compare & pull request"**.
5. No exato instante em que abrir o PR, olhe para os logs do terminal do Docker. Você verá o Jarvis avaliando o código.
6. Volte à tela do GitHub na aba de conversa do PR. O selo ficará vermelho (❌), e você receberá uma rica tabela Markdown detalhando as métricas, além da resposta contextual da LLM analisando o seu código.

*(Para o banco de dados registrar um novo Baseline, clique no botão "Merge pull request" e acompanhe a notificação de Baseline atualizada no console do agente).*
