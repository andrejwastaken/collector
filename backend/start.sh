#!/bin/bash

# Start Ollama server in the background
ollama serve &

# Wait a few seconds for the server to be ready
sleep 10

# Pull the model
ollama pull nomic-embed-text

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload