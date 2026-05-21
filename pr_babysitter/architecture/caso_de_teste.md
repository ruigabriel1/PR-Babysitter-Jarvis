# Caso de Teste: Catraca do Jarvis (PR Babysitter)

## Cenário 1: Reprovação (Catraca Travada)
1. O desenvolvedor abre um Pull Request (PR #10) adicionando uma nova funcionalidade.
2. O webhook do GitHub notifica a rota `POST /webhook` da API do Jarvis.
3. A **Camada de Navegação** (API) extrai o arquivo `.diff` e repassa para a **Camada de Ferramentas**:
   - `tools.linter` roda o Ruff no código, apontando variaveis não utilizadas e falta de type hinting.
   - `tools.quality_gate` avalia que o código inserido reduziu a cobertura de testes de 85% (medida na Baseline do SQLite) para 82%.
4. O *Quality Gate* decide que o PR falhou (`pass: False`).
5. A API invoca a **Skill de Babysit**:
   - Chama `tools.ollama_client` (Ollama/Phi-3) enviando o código e o erro do linter.
   - O Phi-3, assumindo a persona direta do Jarvis, retorna: *"Código com variáveis soltas e redução de cobertura. Correção sugerida:..."*
   - A ferramenta `github_api` posta o comentário *inline* via GitHub API (`POST pulls/10/comments`) exatamente na linha do erro e altera o commit status para `failure` (`REQUEST_CHANGES`).

## Cenário 2: Desbloqueio e Aprovação
1. O desenvolvedor lê a recomendação do Jarvis direto no GitHub, refatora o código e envia um novo commit na mesma branch.
2. O GitHub dispara o evento `synchronize` enviando um novo webhook.
3. A Catraca avalia o novo estado:
   - Cobertura de testes corrigida: 86% (> 85% da Baseline).
   - Zero vulnerabilidades. Zero erros no Linter.
4. O *Quality Gate* calcula a nota final e aprova o envio (`pass: True`).
5. A ferramenta envia a API Call de `APPROVE` no Review e muda o status do commit para `success` verde.
6. A Catraca abre o Pull Request para Merge.
