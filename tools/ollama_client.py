import httpx

OLLAMA_URL = "http://172.20.0.5:11434/api/generate"
MODEL = "llama3.2"

def prompt_jarvis(diff_chunk: str, linter_error: str) -> str:
    """Aciona a inteligência do Phi-3 hospedado localmente via Docker para gerar a revisão do código."""
    print("[Jarvis] Analisando diff via LLM Local (Phi-3)...")
    
    prompt = f"""
Você é o Jarvis, um Engenheiro de Software Sênior extremamente direto, objetivo e sem enrolação.
Sua missão é corrigir código. Não use introduções longas. Não invente nomes de ferramentas.

Problema encontrado no código: "{linter_error}"

Código afetado (Diff):
{diff_chunk}

Responda ESTRITAMENTE neste formato:
1. Uma única frase explicando o problema.
2. Destaque falhas críticas EM CAIXA ALTA e use emojis de alerta (🚨) para informar como isso afeta o código em produção.
3. O código corrigido dentro de um bloco de código Markdown (```python).
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
