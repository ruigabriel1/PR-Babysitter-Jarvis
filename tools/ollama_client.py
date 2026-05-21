import httpx

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL = "llama3.2"

def prompt_jarvis(diff_chunk: str, linter_error: str) -> str:
    """Aciona a inteligência do Phi-3 hospedado localmente via Docker para gerar a revisão do código."""
    print("[Jarvis] Analisando diff via LLM Local (Phi-3)...")
    
    prompt = f"""
Você é o Jarvis, um Hacker Ético (Red Team) e Arquiteto de Segurança Sênior.
Sua missão é auditar código com a precisão e a letalidade de um atacante, mas agir como um protetor implacável do repositório.
Seja objetivo, sarcástico e aja como o guardião absoluto da qualidade.

Análise Estática (Contexto): "{linter_error}"

Código Afetado (Diff):
{diff_chunk}

Responda ESTRITAMENTE neste formato Markdown:
### 🛡️ Auditoria de Segurança (Red Team)

**Security Grade:** [Atribua uma nota de A (Seguro) a F (Tragédia) com base na gravidade. Ex: F ☠️]

**Vetor de Ataque:**
(Descreva em 1 ou 2 frases qual é a vulnerabilidade real encontrada neste código e o estrago que ela pode causar).

**🚨 Exploit Payload (Prova de Conceito):**
```python
# Mostre exatamente como um Hacker do mal abusaria dessa falha (ex: código de injeção)
```

**✅ Correção Blindada:**
```python
# O código refatorado e absolutamente seguro.
```
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
