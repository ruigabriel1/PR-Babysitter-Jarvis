# PR Babysitter (Jarvis) 🤖

               
## Descrição
O PR Babysitter é um Agente Autônomo de Code Review integrado ao fluxo de CI/CD para repositórios GitHub. Ele atua como um Quality Gate automatizado, realizando análises diferenciais de código e fornecendo feedbacks estruturados diretamente nos Pull Requests utilizando inteligência artificial local.

## O Desafio
O desafio técnico consistia em criar um Agente Autônomo capaz de atuar em uma etapa crítica do ciclo de vida de desenvolvimento (SDLC). A principal restrição arquitetural (A.N.T Layer 1) exigia que o modelo de inteligência artificial rodasse de forma 100% local, em ambiente isolado via Docker, garantindo a privacidade absoluta do código corporativo e zero dependência de APIs externas pagas (como OpenAI). O agente precisava não apenas apontar erros, mas bloquear ativamente o envio de código ruim para produção (Quality Gate).

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
- **Cegueira de DNS no Docker/WSL2:** Durante a integração, a API interna falhou na comunicação com a LLM local (`[Errno -2] Name or service not known`). O subsistema Windows (WSL2) muitas vezes entra em conflito com o DNS interno do Docker. **Solução Arquitetural:** Em vez de depender de nomes de host instáveis (`host.docker.internal`), a arquitetura foi refatorada no `docker-compose.yml` para criar uma **Sub-rede Estática (VPC 172.20.0.x)**. Fixamos o IP do Ollama para forçar um roteamento direto (IP-to-IP) a partir da API, garantindo robustez extrema e tolerância a falhas de rede do Host.
- **Orquestração Assíncrona:** O GitHub exige respostas HTTP 200 no webhook em menos de 10 segundos, sob pena de timeout. Como a IA pode levar mais que isso para processar, a arquitetura precisou ser refatorada para utilizar `BackgroundTasks` no FastAPI.

## Melhorias futuras (Caminho de refatoração para produção)
1. **Fim dos Mocks e Integração SAST Real:** Atualmente, a POC do Quality Gate e o LLM consomem números de testes simulados no `api/main.py`. Em produção, o pipeline fará requisições dinâmicas a ferramentas de segurança Enterprise instaladas na pipeline da empresa (SonarQube, Checkmarx).
2. **PostgreSQL Descentralizado:** Transição do SQLite persistido em volume local para um banco de dados transacional relacional AWS RDS, suportando concorrência e múltiplos repositórios simultâneos.
3. **Assinatura Criptográfica:** Blindar a rota do webhook pública validando o payload via `X-Hub-Signature-256`.

## Tutorial de como testar (Deploy "First Try")
O ecossistema foi envelopado em um contêiner *Zero-Config*.

**1. Requisitos Prévios**
- Docker Desktop e Git instalados e em execução.
- Ter configurado um Ngrok para gerar o túnel seguro.
- Possuir uma conta no GitHub e gerar um Personal Access Token (PAT).

**2. O Primeiro Run (First Try)**
Na raiz deste repositório, abra o arquivo **`.env`** (ou copie a partir do `.env.example` se estiver clonando do GitHub) e preencha o seu token:
```env
GITHUB_TOKEN=ghp_SEU_TOKEN_AQUI
```

Execute a subida absoluta dos serviços:
```bash
docker-compose up --build -d
```
> **Nota Mágica:** Você não precisa baixar a IA manualmente. O entrypoint customizado do nosso `docker-compose.yml` fará o Pull de 2.0GB do *Llama 3.2* sozinho antes de abrir a porta da aplicação. Aguarde cerca de 3 minutos.

**3. Tunelamento**
Exponha o container local:
```bash
ngrok http 8000
```
Cadastre o link resultante (`https://seu-link.ngrok-free.app/webhook`) nas configurações do seu repositório no GitHub (*Settings > Webhooks*), assinando os eventos de `Pull request`.

## Caso de Teste Explícito
Siga estes passos exatos para presenciar o Agente reprovando um PR:

1. No seu repositório do GitHub (branch `master`), edite qualquer arquivo de código ou crie um arquivo simples (ex: `teste.py`).
2. Digite a seguinte função propositalmente redundante:
   ```python
   def funcao_abandonada_para_o_jarvis():
       print("Isso vai causar redução de cobertura!")
   ```
3. Crie uma nova branch para isso (`test-jarvis`) e efetue o *Commit*.
4. Abra o **Pull Request** para a branch `master`.
5. Vá para o painel principal do Pull Request. Em menos de 10 segundos, o PR Babysitter identificará o código através do Webhook e calculará o **Quality Gate**. O mock foi desenhado para travar, então ele postará um relatório estruturado avaliando:
   - **Quality Metrics:** Test Coverage, Duplication e Violations (com cálculo de `Δ`).
   - **Code Regressions:** Tamanho do arquivo inflado.
   - **Codex Review:** O LLM (Llama 3.2) fará a auditoria final, berrando em vermelho (`> [!CAUTION] 🚨`) as falhas críticas e fornecendo a refatoração do código sugerida.
