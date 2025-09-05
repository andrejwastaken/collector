FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

# Cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY start.sh .
RUN chmod +x ./start.sh

EXPOSE 8000

# Start Ollama server in the background, then start FastAPI
CMD ["sh", "./start.sh"]

