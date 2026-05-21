from tools.baseline_db import get_current_baseline

def evaluate_quality_gate(pr_coverage: float, pr_duplication: float, pr_violations: int, pr_regression_file: str, pr_regression_lines_before: int, pr_regression_lines_after: int) -> dict:
    """
    Calcula se a catraca deve abrir ou fechar seguindo métricas de qualidade de código.
    Retorna dict com 'pass' (bool), 'reason' (str) e 'report' (str markdown).
    """
    baseline = get_current_baseline()
    
    # Fallback se a db estiver vazia
    base_cov = baseline["test_coverage"] if baseline else 80.0
    base_dup = 2.0
    
    # Formatação de relatório Markdown
    delta_cov = pr_coverage - base_cov
    delta_dup = pr_duplication - base_dup
    
    def formata_sinal(d, is_int=False):
        sinal = "+" if d > 0 else ""
        if is_int:
            return f"{sinal}{d}"
        return f"{sinal}{d:.2f}"

    passed = True
    motivo = "Aprovado nas métricas de qualidade."

    # 1. Regra Absoluta de Violacoes
    if pr_violations > 0:
        passed = False
        motivo = f"Reprovado pela Regra Absoluta: {pr_violations} violação(ões)."
    # 2. Regra Diferencial de Cobertura
    elif pr_coverage < base_cov:
        passed = False
        motivo = f"Reprovado: A cobertura caiu."
    elif pr_duplication > 5.0:
        passed = False
        motivo = f"Reprovado: Duplicação acima de 5%."

    status_icon = "✅ **Passed**" if passed else "❌ **Failed**"
    
    critical_warning = ""
    if pr_violations > 0:
        critical_warning = f"\n> [!CAUTION]\n> 🚨 **FALHA CRÍTICA:** Foram detectadas {pr_violations} violação(ões) severa(s) no seu código. Corrija imediatamente antes de solicitar revisão humana.\n"

    tabela_markdown = f"""### 🛡️ Quality Gate Report
**Status:** {status_icon}
{critical_warning}
#### Quality Metrics

| Metric | Baseline | Current | Δ |
|---|---|---|---|
| **Test Coverage** | {base_cov:.2f}% | {pr_coverage:.2f}% | {formata_sinal(delta_cov)}% |
| **Duplication** | {base_dup:.2f}% | {pr_duplication:.2f}% | {formata_sinal(delta_dup)}% |
| **Violations** | 0 | {pr_violations} | {formata_sinal(pr_violations, True)} |

#### Code Regressions
*O arquivo `{pr_regression_file}` sofreu uma regressão de tamanho. O código originalmente continha **{pr_regression_lines_before}** linhas, e após as suas adições inflou para **{pr_regression_lines_after}** linhas.*

**Motivo do Gate:** {motivo}
"""

    return {
        "pass": passed,
        "reason": motivo, # Texto curto (max 140 chars) para o status check commit
        "report": tabela_markdown.strip() # Texto rico em markdown para o comentário do PR
    }
