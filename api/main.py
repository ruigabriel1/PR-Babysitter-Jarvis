from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from tools.quality_gate import evaluate_quality_gate
from tools.github_api import set_commit_status, submit_pr_review
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
    if action not in ["opened", "synchronize"]:
        return
        
    repo_full_name = payload.get("repository", {}).get("full_name")
    pull_number = pr_data.get("number")
    head_sha = pr_data.get("head", {}).get("sha")
    
    print(f"[Jarvis] Analisando PR #{pull_number}...")
    
    # 1. Altera Status para Pendente
    set_commit_status(repo_full_name, head_sha, "pending", "Jarvis está validando as métricas...")
    
    # 2. Mock de Métricas do Código (Demonstração de Qualidade de Código)
    pr_coverage = 82.0 
    pr_duplication = 3.5
    pr_violations = 1  # Falha crítica proposital
    
    pr_regression_file = "bad_code.py"
    pr_regression_lines_before = 0
    pr_regression_lines_after = 12
    
    # 3. Calcula o Quality Gate
    gate_result = evaluate_quality_gate(pr_coverage, pr_duplication, pr_violations, pr_regression_file, pr_regression_lines_before, pr_regression_lines_after)
    
    if gate_result["pass"]:
        set_commit_status(repo_full_name, head_sha, "success", gate_result["reason"])
        submit_pr_review(repo_full_name, pull_number, "COMMENT", gate_result["report"])
    else:
        set_commit_status(repo_full_name, head_sha, "failure", gate_result["reason"])
        submit_pr_review(repo_full_name, pull_number, "COMMENT", gate_result["report"])
        
        # 4. Aciona a Skill de Babysit via LLM Local
        jarvis_reply = prompt_jarvis(
            diff_chunk="+ def unused_function():\n+    pass\n", 
            linter_error="W0612: Unused variable ou redução de cobertura."
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
