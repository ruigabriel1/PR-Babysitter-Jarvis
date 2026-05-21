# P.O.P - Regra da Catraca (Quality Gate)

## Objetivo
Avaliar se o Pull Request (PR) atual pode ser aprovado e integrado à branch principal, comparando suas métricas estáticas com a Baseline (fonte da verdade guardada no volume isolado).

## Regras
1. **Segurança (Absoluta):** `Vulnerabilidades_Críticas == 0`.
   - Se houver `> 0`, **trava a catraca**. A IA gera comentários imediatos (Babysit).
2. **Cobertura de Teste (Diferencial):** `Cobertura_PR >= Cobertura_Baseline`.
   - Se o PR derrubar o índice de cobertura existente, **trava a catraca**.
3. **Qualidade Ponderada:**
   - Fórmula do PR: `Nota Final = (Seguranca*0.4) + (Complexidade*0.3) + (Boas_Praticas*0.2) + (Erros*0.1)`.
   - Se `Nota Final < 80`, **trava a catraca**.

## Comportamento (Saída)
- **APROVADO (Pass):** Roteia a ação para a API do GitHub alterando o commit status para `success` e criando Review do tipo `APPROVE`.
- **REPROVADO (Fail):** Altera o commit status para `failure`, cria Review `REQUEST_CHANGES` e dispara a skill do Jarvis: comentários "inline" (em cada linha defeituosa) com a correção objetiva gerada pelo Ollama.
