import httpx

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL = "phi3"

def prompt_jarvis(diff_chunk: str, linter_error: str) -> str:
    """Envia o pedaço de código defeituoso para o modelo Phi-3 local e retorna o comentário do Jarvis."""
    prompt = f"""
Você é Jarvis, um assistente especializado em Code Review. Seja extremamente objetivo e direto.
Ocorreu o seguinte erro de qualidade/linter no código: {linter_error}

Código afetado (Diff):
{diff_chunk}

Forneça um feedback para o desenvolvedor explicando o erro em 1 frase e, logo abaixo, forneça a correção no formato de bloco de código.
    """
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        print("[Jarvis] Consultando IA local (Phi-3) para avaliação do código...")
        # Timeout longo para evitar falha no cold start do LLM local
        response = httpx.post(OLLAMA_URL, json=payload, timeout=90.0)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"[Jarvis Error] Conexão com Ollama falhou: {str(e)}")
        return "Erro de análise: O módulo lógico do Jarvis encontra-se offline ou sobrecarregado."
