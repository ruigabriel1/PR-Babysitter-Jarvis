import httpx

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL = "phi3"

def prompt_jarvis(diff_chunk: str, linter_error: str) -> str:
    """Aciona a inteligência do Phi-3 hospedado localmente via Docker para gerar a revisão do código."""
    print("[Jarvis] Analisando diff via LLM Local (Phi-3)...")
    
    prompt = f"""
Você é o Jarvis, um Engenheiro de Software Sênior rígido e objetivo.
O sistema de Quality Gate reprovou um Pull Request e encontrou o seguinte problema:
"{linter_error}"

Abaixo está o trecho de código afetado (Diff):
{diff_chunk}

Sua tarefa:
1. Explique por que isso é um problema.
2. Forneça o bloco de código exato e corrigido, pronto para o desenvolvedor copiar.
"""
    
    payload = {
        "model": MODEL,
        "prompt": prompt.strip(),
        "stream": False
    }
    
    try:
        # Timeout alto (120s) devido ao cold start ou processamento em máquinas sem GPU dedicada
        response = httpx.post(OLLAMA_URL, json=payload, timeout=120.0)
        response.raise_for_status()
        return response.json().get("response", "Erro interno: A LLM não gerou uma resposta válida.")
    except Exception as e:
        return f"[Jarvis System Error] A comunicação com a LLM (Ollama) falhou. Verifique se o container está online. Erro: {str(e)}"
