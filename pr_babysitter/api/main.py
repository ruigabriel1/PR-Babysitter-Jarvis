import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="PR Babysitter API - Jarvis")

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

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    # Lógica de roteamento da Camada 2 (Navegação) entrará aqui
    print(f"[Jarvis] Webhook recebido: {payload.get('action', 'unknown action')}")
    return {"status": "received", "message": "Jarvis está analisando o PR."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
