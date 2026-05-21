import os
import httpx

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def post_inline_comment(repo_full_name: str, pull_number: int, commit_id: str, path: str, line: int, body: str):
    """Cria um comentário na linha exata (Babysit Skill) via GitHub API."""
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pull_number}/comments"
    payload = {
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "line": line,
        "side": "RIGHT"
    }
    response = httpx.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print(f"[Jarvis] Comentário inserido em {path}:{line}.")
    else:
        print(f"[Jarvis Error] Falha ao postar comentário: {response.text}")

def submit_pr_review(repo_full_name: str, pull_number: int, event: str, body: str):
    """Submete uma Review completa (APPROVE ou REQUEST_CHANGES)."""
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pull_number}/reviews"
    payload = {
        "body": body,
        "event": event # 'APPROVE', 'REQUEST_CHANGES', or 'COMMENT'
    }
    response = httpx.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"[Jarvis] PR Review submetido: {event}.")
    else:
        print(f"[Jarvis Error] Falha ao submeter review: {response.text}")

def set_commit_status(repo_full_name: str, sha: str, state: str, description: str):
    """Atualiza a bolinha de status do Commit (success, failure, pending)."""
    url = f"https://api.github.com/repos/{repo_full_name}/statuses/{sha}"
    payload = {
        "state": state,
        "description": description,
        "context": "Jarvis / Quality Gate"
    }
    response = httpx.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print(f"[Jarvis] Status do commit {sha[:7]} alterado para {state}.")
    else:
        print(f"[Jarvis Error] Falha ao alterar status do commit: {response.text}")
