from tools.baseline_db import get_current_baseline

def evaluate_quality_gate(pr_coverage: float, pr_vulns: int, pr_complexity_score: float, pr_best_practices: float, pr_errors_score: float) -> dict:
    """
    Calcula se a catraca deve abrir ou fechar seguindo o POP de arquitetura.
    Retorna dict com 'pass' (bool) e 'reason' (str).
    """
    baseline = get_current_baseline()
    
    # Fallback se a db estiver vazia
    base_cov = baseline.test_coverage if baseline else 0.0
    
    # 1. Regra Absoluta de Seguranca
    if pr_vulns > 0:
        return {
            "pass": False, 
            "reason": f"Reprovado pela Regra Absoluta: {pr_vulns} vulnerabilidade(s) crítica(s) detectada(s)."
        }
        
    # 2. Regra Diferencial de Cobertura
    if pr_coverage < base_cov:
        return {
            "pass": False, 
            "reason": f"Reprovado na Regra Diferencial: A cobertura de testes caiu (Atual: {base_cov}% | PR: {pr_coverage}%)."
        }
        
    # 3. Regra de Qualidade Ponderada
    # Segurança é 100.0 pois passou na regra 1 (0 vulns)
    seguranca_score = 100.0
    
    nota_final = (seguranca_score * 0.4) + (pr_complexity_score * 0.3) + (pr_best_practices * 0.2) + (pr_errors_score * 0.1)
    
    if nota_final >= 80.0:
        return {
            "pass": True, 
            "reason": f"Aprovado. Nota final ponderada: {nota_final:.2f}/100."
        }
    else:
        return {
            "pass": False, 
            "reason": f"Reprovado. A nota do novo código ({nota_final:.2f}/100) não atingiu a média mínima de 80."
        }
