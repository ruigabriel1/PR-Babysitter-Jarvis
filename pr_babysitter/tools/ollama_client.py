import httpx

# OLLAMA_URL = "http://ollama:11434/api/generate"
# MODEL = "phi3"

def prompt_jarvis(diff_chunk: str, linter_error: str) -> str:
    """Mock da IA para rodar sem Docker: Retorna um texto hardcoded do Jarvis."""
    print("[Jarvis] Simulando resposta da IA local (Docker desabilitado)...")
    
    resposta_mock = f"""
Notei que há um problema reportado: `{linter_error}`. 
Além disso, a cobertura de testes foi reduzida!

Por favor, refatore o código adicionando testes ou removendo variáveis inúteis.
```python
# Correção simulada sugerida pelo Jarvis
def codigo_corrigido():
    return "Tudo ok!"
```
    """
    return resposta_mock.strip()
