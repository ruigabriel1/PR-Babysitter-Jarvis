import os
import httpx
from dotenv import load_dotenv

# Carrega o .env manualmente (necessário pois estamos rodando fora do Docker)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
BASE_URL = "https://api.github.com/repos"

import time

def _make_github_request(endpoint: str, payload: dict, success_status: int = 201) -> bool:
    """Função auxiliar para encapsular e evitar código repetido nas chamadas POST da API."""
    url = f"{BASE_URL}/{endpoint}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = httpx.post(url, headers=HEADERS, json=payload, timeout=10.0)
            if response.status_code in (200, 201, success_status):
                return True
            else:
                print(f"[Jarvis Error] Falha na requisição para {endpoint}: {response.text}")
                return False
        except httpx.ConnectError as e:
            print(f"[Jarvis] Erro de conexão (DNS/WSL2): {e}. Tentativa {attempt + 1}/{max_retries}. Retentando...")
            time.sleep(2)
        except Exception as e:
            print(f"[Jarvis Error] Exceção desconhecida: {e}")
            return False
            
    return False

def post_inline_comment(repo_full_name: str, pull_number: int, commit_id: str, path: str, line: int, body: str):
    """Cria um comentário na linha exata (Babysit Skill) via GitHub API."""
    payload = {
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "line": line,
        "side": "RIGHT"
    }
    if _make_github_request(f"{repo_full_name}/pulls/{pull_number}/comments", payload):
        print(f"[Jarvis] Comentário inserido em {path}:{line}.")

def submit_pr_review(repo_full_name: str, pull_number: int, event: str, body: str):
    """Submete uma Review completa (APPROVE ou REQUEST_CHANGES)."""
    payload = {
        "body": body,
        "event": event # 'APPROVE', 'REQUEST_CHANGES', or 'COMMENT'
    }
    if _make_github_request(f"{repo_full_name}/pulls/{pull_number}/reviews", payload, success_status=200):
        print(f"[Jarvis] PR Review submetido: {event}.")

def set_commit_status(repo_full_name: str, sha: str, state: str, description: str):
    """Atualiza a bolinha de status do Commit (success, failure, pending)."""
    payload = {
        "state": state,
        "description": description,
        "context": "Jarvis / Quality Gate"
    }
    if _make_github_request(f"{repo_full_name}/statuses/{sha}", payload):
        print(f"[Jarvis] Status do commit {sha[:7]} alterado para {state}.")

def get_pr_diff(repo_full_name: str, pull_number: int) -> str:
    """Busca o Diff cru (unified) do Pull Request na API do GitHub com sistema de retentativa."""
    url = f"{BASE_URL}/{repo_full_name}/pulls/{pull_number}"
    
    headers = HEADERS.copy()
    headers["Accept"] = "application/vnd.github.v3.diff"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = httpx.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                return response.text
            else:
                print(f"[Jarvis Error] Falha ao buscar Diff: {response.status_code} - {response.text}")
                return ""
        except httpx.ConnectError as e:
            print(f"[Jarvis] Erro de conexão (DNS/WSL2) ao buscar Diff: {e}. Tentativa {attempt + 1}/{max_retries}. Retentando...")
            time.sleep(2)
        except Exception as e:
            print(f"[Jarvis Error] Exceção desconhecida ao buscar Diff: {e}")
            return ""
            
    return ""
