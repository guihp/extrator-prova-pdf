#!/bin/bash

# Script de inicialização do backend
# Este script inicia o servidor FastAPI e o worker Celery

echo "🚀 Iniciando Sistema de Análise de PDFs - Backend"
echo ""

# Criar diretórios se não existirem
mkdir -p uploads images

# Iniciar Celery Worker em background
echo "📦 Iniciando Celery worker..."
celery -A app.tasks worker --loglevel=info --pool=solo &
CELERY_PID=$!

# Aguardar um pouco para o Celery inicializar
sleep 3

# Iniciar FastAPI
echo "🌐 Iniciando servidor FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Se o uvicorn parar, parar também o Celery
kill $CELERY_PID 2>/dev/null

