# PR Babysitter (Jarvis)

Agente Autônomo de Code Review integrado ao fluxo de CI/CD para repositórios GitHub. O PR Babysitter atua como um Quality Gate automatizado, realizando análises diferenciais de código e fornecendo feedbacks estruturados diretamente nos Pull Requests utilizando inteligência artificial local (Llama 3.2).

## Arquitetura e Componentes

O agente foi desenvolvido com foco em determinismo, baixa latência e segurança, adotando o protocolo estrutural de 3 camadas:

- **Camada de Orquestração (FastAPI):** Gerencia a recepção de webhooks (`opened`, `synchronize`, `closed`) de forma assíncrona, garantindo resiliência contra timeouts da API do GitHub.
- **Camada de Análise (Quality Gate):** Implementa regras de negócio estritas (vulnerabilidades, cobertura de testes e complexidade ciclomática) baseadas em deltas (`Δ`). O código não é promovido à branch principal caso degrade as métricas atuais (Baseline).
- **Camada Cognitiva (LLM Local):** Utiliza o modelo Llama 3.2 empacotado via Docker/Ollama para fornecer análises de código (*code reviews*) interpretativas e sugerir refatorações pontuais no formato de comentários *inline*.

### Armazenamento da Baseline
Para manter o estado do repositório íntegro e imutável durante as avaliações do Pull Request, a fonte da verdade das métricas (Baseline) é armazenada em um banco de dados SQLite persistido no volume Docker. A Baseline é retroalimentada unicamente mediante a interceptação do evento de *Merge* consolidado na branch `master`.

## Requisitos de Infraestrutura

- **Docker & Docker Compose:** Obrigatório para a orquestração do ecossistema e isolamento dos serviços (API + Ollama).
- **Recursos Computacionais:** Recomenda-se alocação mínima de 8GB de RAM para estabilidade inferencial do modelo Llama 3.2.
- **GitHub Personal Access Token (PAT):** Token Clássico do GitHub, configurado com privilégios completos sob o escopo `repo`, para conceder permissões de leitura/escrita na Commit Status API e publicação de Pull Request Reviews.

## Deploy e Inicialização

O sistema foi arquitetado para *plug and play* em ambientes conteinerizados, eliminando fricções de dependências sistêmicas.

1. **Configuração de Variáveis de Ambiente:**
   Defina o arquivo `.env` na raiz da aplicação com o token de serviço do GitHub:
   ```env
   GITHUB_TOKEN=ghp_SEU_TOKEN_DE_SERVICO
   ```

2. **Subida dos Serviços (First Try / Zero-Config):**
   A arquitetura garante execução *First Try* sem a necessidade de downloads paralelos ou acionamentos manuais do Ollama. Realize a subida consolidada:
   ```bash
   docker-compose up --build -d
   ```
   *Nota: No primeiro start-up, o entrypoint customizado do Docker fará automaticamente o `pull` da imagem do Llama 3.2 e inicializará a API em cascata.*

3. **Configuração do Webhook no Repositório:**
   - Exponha o serviço na porta `8000` via Ingress, API Gateway ou túnel seguro.
   - Navegue até as configurações do repositório alvo (`Settings > Webhooks`) e cadastre a rota pública finalizada em `/webhook`.
   - Content type: `application/json`.
   - Eventos inscritos: `Pull requests`.

## Orientações e Fluxo de Operação

- **Bloqueios de Merge Institucionais:** A API atualizará continuamente o Status Check do GitHub. Recomenda-se fortemente habilitar a proteção de branch na `master` (*Require status checks to pass before merging*), atrelando o merge exclusivamente à aprovação da pipeline do Agente.
- **Auto-Aprovação de Pull Requests:** O bot emite os vereditos estruturados atrelados à tag de evento `COMMENT` em vez de `APPROVE` / `REQUEST_CHANGES`. Isso garante compatibilidade corporativa universal, prevenindo restrições nativas da API do GitHub referentes a *Self-Review* nos casos em que a identidade executora for a mesma do autor do código.

## Roteiro de Escalabilidade

Para a adoção extensiva em ambiente de Produção, indica-se a aplicação das seguintes adequações:
1. **Integração SAST/DAST Real (Fim dos Mocks):** Para tornar a avaliação do Agente 100% utilitária no mundo real, é necessário substituir os valores numéricos fixos de demonstração (Mock) presentes no arquivo `api/main.py` por integrações dinâmicas a parsers ou webhooks de ferramentas enterprise de análise estática (ex: SonarQube, Checkmarx, Fortify). A matemática do Quality Gate já está pronta e provada, basta "ligar os canos" para plugar as métricas reais.
2. **Armazenamento Descentralizado:** Transição do SQLite de volume local para clusters PostgreSQL ou MySQL gerenciados (ex: AWS RDS), habilitando concorrência multi-repositório no mesmo Agente.
3. **Assinatura Criptográfica:** Implementação do mecanismo `X-Hub-Signature-256` no FastAPI, blindando a rota de recepção pública de payloads de origem não certificada.
