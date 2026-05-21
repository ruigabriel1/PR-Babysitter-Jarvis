FROM python:3.11-slim

WORKDIR /app

# Dependencia do git e ferramentas basicas
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiando todo o resto do repositorio
COPY . .

# Garantir que os modulos locais como tools e api possam ser importados globalmente
ENV PYTHONPATH=/app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
