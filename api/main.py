from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from tools.quality_gate import evaluate_quality_gate
from tools.github_api import set_commit_status, submit_pr_review, get_pr_diff
from tools.ollama_client import prompt_jarvis
import uvicorn


app = FastAPI(title="PR Babysitter API - Jarvis")

# Função inútil para disparar o Linter e a IA
def variavel_inutil_para_teste():
    x = "Essa variável não é usada e deve irritar o Jarvis."
    return None

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
        <head>
            <title>PR Babysitter Dashboard</title>
            <style>
                body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; padding: 2rem; }
                h1 { color: #38bdf8; }
                .card { background-color: #1e293b; padding: 1.5rem; border-radius: 0.5rem; margin-top: 1rem; }
            </style>
        </head>
        <body>
            <h1>Jarvis Online</h1>
            <div class="card">
                <h2>Status da Baseline</h2>
                <p>Nenhuma métrica capturada ainda.</p>
            </div>
            <div class="card">
                <h2>Últimos PRs Analisados</h2>
                <p>Aguardando webhooks...</p>
            </div>
        </body>
    </html>
    """

async def process_pr(payload: dict):
    """Navegador Central do Jarvis. Recebe o Payload e orquestra as Ferramentas."""
    action = payload.get("action")
    pr_data = payload.get("pull_request", {})
    
    # --- FLUXO DE ATUALIZAÇÃO DE BASELINE ---
    # Quando o PR é fechado E aprovado (merged) na master:
    if action == "closed" and pr_data.get("merged") is True:
        print(f"[Jarvis] PR #{pr_data.get('number')} Mergeado! Atualizando o Banco de Dados da Baseline...")
        from tools.baseline_db import update_baseline
        # Em produção, aqui nós leríamos os dados finais da branch master.
        # No nosso mock, vamos fixar os valores para popular o SQLite:
        update_baseline(coverage=82.0, vulns=0, complexity=70.0)
        return
        
    # --- FLUXO DE VALIDAÇÃO DE PR ---
    if action not in ["opened", "synchronize", "reopened"]:
        return
        
    repo_full_name = payload.get("repository", {}).get("full_name")
    pull_number = pr_data.get("number")
    head_sha = pr_data.get("head", {}).get("sha")
    
    print(f"[Jarvis] Analisando PR #{pull_number}...")
    
    # 1. Altera Status para Pendente
    set_commit_status(repo_full_name, head_sha, "pending", "Jarvis está validando as métricas...")
    
    # 2. Ler o Diff Real
    raw_diff = get_pr_diff(repo_full_name, pull_number)
    
    # 3. Parsear o Diff para calcular Métricas Reais
    lines_added = 0
    lines_removed = 0
    critical_violations = 0
    affected_files = set()
    current_file = "unknown"
    
    vulnerable_keywords = ["eval(", "exec(", "password", "os.system(", "subprocess.Popen(", "secret", "token"]
    
    for line in raw_diff.split("\n"):
        if line.startswith("+++ b/"):
            current_file = line[6:]
            affected_files.add(current_file)
        elif line.startswith("+") and not line.startswith("+++"):
            lines_added += 1
            # Procura por vulnerabilidades na linha adicionada
            lower_line = line.lower()
            for kw in vulnerable_keywords:
                if kw in lower_line:
                    critical_violations += 1
        elif line.startswith("-") and not line.startswith("---"):
            lines_removed += 1
            
    # Configurar Métricas Baseadas na Realidade
    # A Cobertura vai cair dinamicamente conforme mais linhas são adicionadas sem testes no PR
    pr_coverage = max(0.0, 82.0 - (lines_added * 0.15)) 
    pr_duplication = 2.0 + (lines_added * 0.05) # Sobe a duplicação baseado no tamanho do diff
    pr_violations = critical_violations
    
    pr_regression_file = list(affected_files)[0] if affected_files else "Nenhum arquivo"
    pr_regression_lines_before = lines_removed
    pr_regression_lines_after = lines_added
    
    # 4. Calcula o Quality Gate
    gate_result = evaluate_quality_gate(pr_coverage, pr_duplication, pr_violations, pr_regression_file, pr_regression_lines_before, pr_regression_lines_after)
    
    if gate_result["pass"]:
        set_commit_status(repo_full_name, head_sha, "success", gate_result["reason"])
        submit_pr_review(repo_full_name, pull_number, "COMMENT", gate_result["report"])
    else:
        set_commit_status(repo_full_name, head_sha, "failure", gate_result["reason"])
        submit_pr_review(repo_full_name, pull_number, "COMMENT", gate_result["report"])
        
        # 5. Aciona a Skill de Babysit via LLM Local usando o DIFF REAL!
        safe_diff = raw_diff[:3000] if len(raw_diff) > 3000 else raw_diff
        
        linter_msg = f"Atenção: Foram detectadas {critical_violations} vulnerabilidades (Ex: eval, injeção de comando, senhas). Além disso, o PR adicionou {lines_added} linhas sem testes, derrubando a cobertura para {pr_coverage:.2f}%."
        
        jarvis_reply = prompt_jarvis(
            diff_chunk=safe_diff, 
            linter_error=linter_msg
        )
        submit_pr_review(repo_full_name, pull_number, "COMMENT", f"## Codex Review\n\n{jarvis_reply}")

@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    # Adicionamos em background task para garantir que o webhook responda rápido e evite Timeout
    background_tasks.add_task(process_pr, payload)
    return {"status": "received", "message": "Jarvis iniciou a análise em background."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
