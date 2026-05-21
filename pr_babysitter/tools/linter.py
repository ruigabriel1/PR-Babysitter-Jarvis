import subprocess
import json
import os

def run_ruff_linter(file_path: str) -> list:
    """Roda o Ruff linter no arquivo e retorna lista de erros com linha e mensagem."""
    if not os.path.exists(file_path):
        return []
        
    try:
        # ruff check file_path --format json
        result = subprocess.run(
            ['ruff', 'check', file_path, '--format', 'json'],
            capture_output=True,
            text=True
        )
        if not result.stdout.strip():
            return []
            
        errors = json.loads(result.stdout)
        formatted_errors = []
        for err in errors:
            formatted_errors.append({
                "line": err["location"]["row"],
                "message": err["message"],
                "code": err["code"]
            })
        return formatted_errors
    except Exception as e:
        print(f"[Jarvis Error] Erro ao executar linter em {file_path}: {e}")
        return []
