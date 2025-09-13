#!/bin/bash

ollama serve &

sleep 10

ollama pull bge-m3 && ollama pull llama3.2:1b

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

streamlit run /app/frontend.py --server.port 8501 --server.address 0.0.0.0