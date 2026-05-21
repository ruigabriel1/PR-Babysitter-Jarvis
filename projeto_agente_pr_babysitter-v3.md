# Projeto: Agente Autônomo de Code Review e PR Babysitter

Este documento consolida as diretrizes do desafio técnico para a Banca do DITEC (Softplan), definindo o escopo, a arquitetura avançada de métricas e as regras de negócio do agente autônomo.

---

## 1. Visão Geral do Agente
O **PR Babysitter** é um agente de IA autônomo projetado para atuar no ecossistema de integração contínua (CI/CD), assumindo o papel de um revisor técnico sênior. Ele gerencia o ciclo de vida de Pull Requests (PRs) de ponta a ponta, avaliando a qualidade do código através de análises determinísticas e heurísticas, guiando o desenvolvedor nas correções e interagindo diretamente com a API do repositório de forma independente.

---

## 2. Capacidades Centrais & Skill de "Babysit"

O diferencial deste agente é a sua habilidade de realizar o **"babysit" do Pull Request**, eliminando o microgerenciamento de código por parte dos Tech Leads.

### Fluxo Operacional de Correção:
1. **Gatilho (Trigger):** O agente intercepta webhooks enviados pelo GitHub/GitLab assim que um PR é aberto ou atualizado (`synchronize`).
2. **Coleta e Análise Estática:** Realiza o download do arquivo `.diff` e executa ferramentas de linting/análise estática (ex: Pylint, Ruff, SonarQube) de forma headless via container.
3. **Análise de IA (Contextual):** Envia o diff e os relatórios estáticos para a LLM estruturar as falhas em categorias.
4. **Interação Inline (Babysit):** O agente insere comentários diretamente nas linhas afetadas do código no GitHub, explicando detalhadamente o problema e fornecendo o bloco de código corrigido (*Suggested Changes*).
5. **Resolução de Conversas Automatizada:** O agente monitora novas atualizações. Assim que o desenvolvedor realiza um novo commit que endereça e corrige o problema apontado, o agente **resolve automaticamente a thread da conversa** no PR, mantendo o histórico limpo.

---

## 3. Mecanismo de Baseline (Análise Diferencial)

Para garantir que o agente funcione como um motor de melhoria contínua de nível corporativo, ele adota o conceito de **Análise Diferencial**. O foco não é exigir perfeição imediata de códigos legados, mas sim garantir que **o código novo não piore o estado atual do repositório**.

### Gerenciamento de Estado da Baseline:
* **Armazenamento Isolado:** As métricas oficiais da branch principal (`main`/`develop`) são salvas em um banco de dados leve ou volume isolado controlado pelo agente (dentro do ambiente Docker), impedindo que desenvolvedores alterem ou burlem os dados de comparação no próprio PR.
* **Evolução da Régua (Webhook de Push):** O agente escuta o evento de `push` ou `merge` na branch principal. Quando um PR é integrado com sucesso, o agente roda silenciosamente sobre a branch principal, calcula a nova "foto" de métricas do sistema e **sobrescreve a Baseline antiga**, elevando o nível de exigência para os próximos PRs.

---

## 4. O Quality Gate (A "Catraca" do PR)

O **Quality Gate** funciona como a catraca de segurança que decide o destino do PR. A aprovação não depende de uma IA tentando adivinhar uma nota arbitrária, mas sim de validações matemáticas booleanas rígidas que cruzam os dados do PR atual ($M_{pr}$) com os dados históricos guardados na Baseline ($M_{baseline}$).

### Regras de Avaliação da Catraca:

1. **Regra de Segurança (Absoluta):**
   $$\text{Vulnerabilidades Críticas do PR} == 0$$
   *Qualquer falha grave de segurança (ex: injeção de SQL ou chaves expostas) trava a catraca imediatamente.*

2. **Regra de Cobertura de Testes (Diferencial):**
   $$\text{Cobertura do PR } (M_{pr}) \ge \text{ Cobertura da Baseline } (M_{baseline})$$
   *O código novo enviado não pode reduzir o percentual de cobertura de testes existente no projeto.*

3. **Regra de Complexidade e Débito Técnico (Ponderada):**
   A IA avalia o código e calcula uma nota ponderada para o novo incremento usando a fórmula:
   $$\text{Nota Final} = (\text{Segurança} \times 0.4) + (\text{Complexidade} \times 0.3) + (\text{Boas Práticas} \times 0.2) + (\text{Tratamento de Erros} \times 0.1)$$
   * **Se Nota Final $\ge$ 80 E passar nas Regras 1 e 2:** A catraca abre. O agente executa a aprovação (`APPROVE`) via API e permite o fluxo de deploy.
   * **Se Nota Final < 80 OU falhar em qualquer Regra:** A catraca trava. O agente bloqueia o merge, altera o status para `Request Changes` e dispara a *skill de babysit* inline explicando exatamente qual métrica causou a reprovação.

---

## 5. Entregáveis Obrigatórios da Solução

* **README.md na Raiz:** Descrição, justificativa das propostas e escolhas técnicas, pontos aprendidos, plano de refatoração para produção e tutorial de execução.
* **docker-compose.yml na Raiz:** Configuração para subir a API do agente, as dependências do linter, o banco de dados (SQLite) para a baseline e um container do **Ollama (rodando Phi-3)**. Deve funcionar *first try* em uma máquina limpa.
* **Caso de Teste Explícito:** Guia passo a passo simulando a abertura de um PR com métricas inferiores à baseline para demonstrar a catraca travando, e o posterior desbloqueio após as correções.
* **.env Funcional:** Arquivo de configuração contendo as chaves obrigatórias (apenas `GITHUB_TOKEN`, já que a LLM será local via Ollama).
