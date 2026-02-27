FROM python:3.12-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os requerimentos primeiro para usar o cache da camada do Docker
COPY requirements.txt .

# Instalar dependências limpas
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código fonte para dentro do container
COPY . .

# Expor a porta padrão do uvicorn
EXPOSE 8000

# Comando final (A versão de dev no docker-compose vai sobrescrever com --reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
