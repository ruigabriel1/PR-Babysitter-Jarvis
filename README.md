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
> **Nota Mágica:** Você não precisa baixar a IA manualmente. O entrypoint customizado fará o Pull automático de 2GB do *Llama 3.2* e iniciará o servidor da API. O `smee-client` também subirá automaticamente em background, conectando a sua máquina local diretamente aos Webhooks do meu repositório no GitHub de forma transparente! Aguarde ~3 minutos.

## Caso de Teste Explícito (Prova de Fogo)
O Agente atua no **Mundo Real**. Ele faz o download dinâmico do Diff, calcula as regressões matemáticas, e o Llama 3.2 atua encarnando uma persona de **Hacker Ético (Red Team)** para auditar vulnerabilidades.

Siga estes passos exatos para testar o Agente rodando na sua máquina:

1. O Docker já deve estar rodando localmente (veja o passo acima).
2. Acesse o meu repositório oficial no GitHub: [https://github.com/ruigabriel1/PR-Babysitter-Jarvis](https://github.com/ruigabriel1/PR-Babysitter-Jarvis)
3. Para conseguir enviar código para o meu repositório sem precisar fazer um Fork, você utilizará o meu próprio Token (que já está no arquivo `.env` que você descompactou).
4. No seu terminal, clone o repositório utilizando o Token embutido na URL de autenticação:
   ```bash
   git clone https://<COLE_O_TOKEN_DO_ENV_AQUI>@github.com/ruigabriel1/PR-Babysitter-Jarvis.git
   ```
5. Entre na pasta clonada e crie uma nova branch:
   ```bash
   cd PR-Babysitter-Jarvis
   git checkout -b teste-banca-avaliadora
   ```
6. Copie e cole todo o conteúdo do arquivo `evaluator_test_template.py` para dentro de um arquivo novo qualquer. *(Esse template contém uso malicioso de `eval`, `os.system`, senhas expostas e código inútil para explodir a duplicação).*
7. Efetue o *Commit* e o *Push* diretamente para o meu repositório:
   ```bash
   git add .
   git commit -m "Teste de invasão"
   git push origin teste-banca-avaliadora
   ```
8. Acesse a página do repositório no GitHub e abra um **Pull Request**.
9. **A Magia:** Vá para a aba do Pull Request no meu repositório. Como o GitHub disparou o Webhook para o Smee, a API *rodando na sua máquina física* receberá o payload, processará o Diff com o Llama 3.2 local, e usará o Token embutido no `.env` para postar a resposta de volta no GitHub!
10. Em poucos segundos, você verá:
   - As **Tabelas de Quality Gate** (Coverage penalizada, Duplication e Violations).
   - O veredito de falha (*Failed*).
   - O **Dossiê do Red Team** gerado pela IA contendo a Nota de Segurança (Security Grade), o Vetor de Ataque e um *Exploit Payload* simulando o ataque real.
