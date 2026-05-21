import os
import httpx

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
BASE_URL = "https://api.github.com/repos"

def _make_github_request(endpoint: str, payload: dict, success_status: int = 201) -> bool:
    """Função auxiliar para encapsular e evitar código repetido nas chamadas POST da API."""
    url = f"{BASE_URL}/{endpoint}"
    response = httpx.post(url, headers=HEADERS, json=payload)
    if response.status_code in (200, 201, success_status):
        return True
    else:
        print(f"[Jarvis Error] Falha na requisição para {endpoint}: {response.text}")
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
