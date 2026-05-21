from tools.baseline_db import get_current_baseline

def evaluate_quality_gate(pr_coverage: float, pr_vulns: int, pr_complexity_score: float, pr_best_practices: float, pr_errors_score: float) -> dict:
    """
    Calcula se a catraca deve abrir ou fechar seguindo o POP de arquitetura.
    Retorna dict com 'pass' (bool) e 'reason' (str).
    """
    baseline = get_current_baseline()
    
    # Fallback se a db estiver vazia
    base_cov = baseline["test_coverage"] if baseline else 0.0
    
    # Formatação de relatório Markdown
    delta_cov = pr_coverage - base_cov
    delta_vulns = pr_vulns - (baseline["critical_vulns"] if baseline else 0)
    delta_comp = pr_complexity_score - (baseline["complexity_score"] if baseline else 0.0)
    
    def formata_sinal(d, is_int=False):
        sinal = "+" if d > 0 else ""
        if is_int:
            return f"{sinal}{d}"
        return f"{sinal}{d:.2f}"

    passed = True
    motivo = ""

    # 1. Regra Absoluta de Seguranca
    if pr_vulns > 0:
        passed = False
        motivo = f"Reprovado pela Regra Absoluta: {pr_vulns} vuln(s) crítica(s)."
    # 2. Regra Diferencial de Cobertura
    elif pr_coverage < base_cov:
        passed = False
        motivo = f"Reprovado na Regra Diferencial: A cobertura caiu."
    else:
        # 3. Regra de Qualidade Ponderada
        seguranca_score = 100.0
        nota_final = (seguranca_score * 0.4) + (pr_complexity_score * 0.3) + (pr_best_practices * 0.2) + (pr_errors_score * 0.1)
        if nota_final >= 80.0:
            passed = True
            motivo = f"Aprovado. Nota final ponderada: {nota_final:.2f}/100."
        else:
            passed = False
            motivo = f"Reprovado. Nota ({nota_final:.2f}/100) abaixo da média 80."

    status_icon = "✅ **Passed**" if passed else "❌ **Failed**"
    
    tabela_markdown = f"""### 🛡️ Quality Gate Report
**Status:** {status_icon}

| Metric | Baseline | Current | Δ |
|---|---|---|---|
| **Test Coverage** | {base_cov:.2f}% | {pr_coverage:.2f}% | {formata_sinal(delta_cov)}% |
| **Critical Vulns** | {(baseline["critical_vulns"] if baseline else 0)} | {pr_vulns} | {formata_sinal(delta_vulns, True)} |
| **Complexity Score**| {(baseline["complexity_score"] if baseline else 0.0):.2f} | {pr_complexity_score:.2f} | {formata_sinal(delta_comp)} |

**Motivo:** {motivo}
"""

    return {
        "pass": passed,
        "reason": motivo, # Texto curto (max 140 chars) para o status check commit
        "report": tabela_markdown.strip() # Texto rico em markdown para o comentário do PR
    }
