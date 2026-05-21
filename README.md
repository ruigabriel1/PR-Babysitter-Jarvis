# PR Babysitter (Jarvis) 🤖
        
## Descrição
O PR Babysitter é um Agente Autônomo de Code Review integrado ao fluxo de CI/CD para repositórios GitHub. Ele atua como um Quality Gate automatizado, realizando análises diferenciais de código e fornecendo feedbacks estruturados diretamente nos Pull Requests utilizando inteligência artificial local.

## O Desafio
O desafio técnico consistia em criar um Agente Autônomo capaz de atuar em uma etapa crítica do ciclo de vida de desenvolvimento (SDLC). A principal restrição arquitetural (A.N.T Layer 1) exigia que o modelo de inteligência artificial rodasse de forma 100% local, em ambiente isolado via Docker, garantindo a privacidade absoluta do código corporativo e zero dependência de APIs externas pagas (como OpenAI). O agente precisava não apenas apontar erros, mas bloquear ativamente o envio de código ruim para produção (Quality Gate).

> [!NOTE] 
> ### Contexto da Entrega (Nota do Autor)
> Este projeto foi idealizado, desenhado e executado em **menos de 24 horas**, utilizando exclusivamente um ecossistema de ferramentas gratuitas e sem depender de nenhum recurso empresarial ou cloud corporativa privada (aos quais eu não tinha acesso). 
> 
> A arquitetura deste agente autônomo foi construída de ponta a ponta em sinergia com o **Antigravity**. Apesar do ambiente de restrição (hardware local, LLM de 3B parâmetros e APIs gratuitas), o **Jarvis** foi arquitetado com *Design Patterns* agnósticos. Isso significa que ele é um motor 100% escalável e configurável. Em um ambiente corporativo dotado de recursos adequados, ele pode ser plulgado a modelos colossais (GPT-4, Claude), integrado a pipelines maduros e configurado para auditar massivamente qualquer base de código e linguagem.

## A Solução
A solução foi arquitetada em 3 camadas de orquestração:
1. **Camada de Orquestração (FastAPI):** Um servidor web assíncrono que intercepta eventos do GitHub (via Webhooks).
2. **Camada de Análise (Quality Gate):** Um motor matemático que calcula métricas diferenciais (`Δ`) de Cobertura, Segurança e Complexidade. O sistema usa um banco de dados **SQLite** embarcado para manter a "Baseline" da branch `master`.
3. **Camada Cognitiva (Ollama + Llama 3.2):** O coração da inteligência. Um LLM leve e altamente capaz, rodando internamente no Docker, que recebe os *diffs* reprovados e posta as correções *inline* como um engenheiro Sênior.

## Justificativa das propostas e escolhas técnicas
- **LLM Escolhido (Llama 3.2):** Inicialmente testado com Phi-3, o agente foi migrado para o recém-lançado Llama 3.2 (3 Bilhões de parâmetros) para entregar Code Reviews mais assertivas, sem alucinações, e ainda mantendo um consumo baixo de RAM (cerca de 2GB) para suportar execução em hardware padrão.
- **Engenharia de Prompt (Dictatorial):** O prompt do LLM foi formatado de forma rígida para gerar saídas estritas contendo apenas: 1 frase de diagnóstico, 1 frase de nível de criticidade e 1 bloco Markdown. Isso eliminou a verbosidade clássica dos modelos menores.
- **Estratégia de Status Check ("COMMENT" vs "REQUEST_CHANGES"):** Para contornar a limitação de API do GitHub que proíbe "Self-Reviews", o agente foi programado para injetar regras via eventos `COMMENT`, sincronizando o veredito (Pass/Fail) com o painel de *Commit Status Check*, habilitando a proteção efetiva de branches corporativas.

## Pontos aprendidos
- Entendimento profundo sobre as barreiras da Virtualização (WSL2) no Windows, especificamente em relação à perda de resolução de DNS interno de containers que afeta requisições SSL externas.
- Práticas avançadas de Prompt Engineering necessárias para extrair formatação de código impecável (Markdown) de LLMs menores (sub-5B).

## Dificuldades

- **Orquestração Assíncrona:** O GitHub exige respostas HTTP 200 no webhook em menos de 10 segundos, sob pena de timeout. Como a IA pode levar mais que isso para processar, a arquitetura precisou ser refatorada para utilizar `BackgroundTasks` no FastAPI.

## Melhorias futuras (Caminho de refatoração para produção)
1. **Integração SAST/DAST Real:** Atualmente, o Quality Gate avalia a segurança varrendo o Diff em tempo real atrás de vetores de vulnerabilidade. Em uma refatoração para produção corporativa, o pipeline poderá ser acoplado para fazer requisições dinâmicas a ferramentas de segurança Enterprise (SonarQube, Checkmarx) para injetar as métricas de `Violations` com maior precisão estática.
2. **PostgreSQL Descentralizado:** Transição do SQLite persistido em volume local para um banco de dados transacional relacional AWS RDS, suportando concorrência e múltiplos repositórios simultâneos.
3. **Assinatura Criptográfica:** Blindar a rota do webhook pública validando o payload via `X-Hub-Signature-256`.

## Tutorial de como testar (Deploy "First Try")
Pensando na Banca Avaliadora, o ecossistema foi projetado com uma arquitetura **Zero-Config**. 
Você não precisa criar Tokens, não precisa configurar Webhooks, não precisa de Ngrok e não precisa alterar nenhuma variável. O arquivo `.zip` já foi entregue contendo um `.env` **100% funcional**, injetado com um PAT de acesso restrito e o túnel na nuvem (`smee.io`) pré-configurado.

**1. Requisitos Prévios**
- Docker Desktop instalado e em execução.
- Conta no GitHub.

**2. O Primeiro Run (First Try)**
Extraia o `.zip` da entrega e, no diretório raiz, execute a subida dos serviços:
```bash
docker-compose up --build -d
```
> **Processo de Inicialização (Automático):** O *entrypoint* do contêiner fará o download da imagem do *Llama 3.2* (~2GB) e subirá o servidor FastAPI em conjunto com o `smee-client` (para roteamento seguro de webhooks). Todo o fluxo de provisionamento e tunelamento ocorre automaticamente. Aguarde aproximadamente 3 minutos para a estabilização dos serviços.

## Caso de Teste Explícito: Auditoria Dinâmica e Qualidade de Código
O PR Babysitter opera processando dados reais do Pull Request. O agente executa o download do *Diff* remoto, processa métricas quantitativas de regressão (Quality Gate) e aciona a IA para realizar uma auditoria focada em segurança da informação (Red Team).

Siga as etapas abaixo para validar o fluxo end-to-end do agente rodando a partir do seu ambiente local:

1. Certifique-se de que os serviços do Docker já estão em execução (conforme passo anterior).
2. No terminal, clone o repositório original utilizando o PAT fornecido no arquivo `.env`. Isso garante a permissão de envio (Push) direto para o repositório base sem a necessidade de criação de um Fork:
   ```bash
   git clone https://<COLE_O_TOKEN_DO_ENV_AQUI>@github.com/ruigabriel1/PR-Babysitter-Jarvis.git
   ```
3. Acesse o diretório clonado e isole o ambiente de teste em uma nova branch:
   ```bash
   cd PR-Babysitter-Jarvis
   git checkout -b teste-auditoria-agente
   ```
4. Crie um novo script na raiz do projeto (ex: `analise_risco.py`) e cole todo o conteúdo do arquivo `evaluator_test_template.py`. Este *template* contém intencionalmente violações graves de segurança (uso de `eval`, chamadas `os.system` e credenciais *hardcoded*), além de instruções vazias para forçar quedas matemáticas de cobertura.
5. Submeta as alterações para o repositório remoto:
   ```bash
   git add .
   git commit -m "Teste: Submissão de código vulnerável"
   git push origin teste-auditoria-agente
   ```
6. Acesse o repositório oficial no GitHub ([PR-Babysitter-Jarvis](https://github.com/ruigabriel1/PR-Babysitter-Jarvis)) e proceda com a abertura de um **Pull Request**.
7. **Validação do Pipeline:** A criação do PR acionará o Webhook público. O evento será roteado pelo `smee.io` até a sua infraestrutura Docker local, onde o *Diff* será decodificado, analisado pelo *Llama 3.2* e o relatório de auditoria será devolvido ao GitHub através do Token configurado no container.
8. Retorne à aba do seu Pull Request. Em poucos segundos, o Agente postará:
   - **Quality Gate Metrics:** Tabelas com a penalização matemática no *Coverage*, métricas de *Duplication* e contagem de *Violations*.
   - **Red Team Dossier:** Um laudo de segurança emitido pela IA contendo a nota de risco (*Security Grade*), a análise técnica do vetor de ataque e um *Exploit Payload* simulando como o código seria comprometido.
