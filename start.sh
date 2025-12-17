#!/bin/bash

echo "🚀 Iniciando Sistema de Análise de PDFs"
echo ""

# Verificar se Redis está rodando
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis não está rodando!"
    echo "   Inicie o Redis primeiro:"
    echo "   - Docker: docker run -d -p 6379:6379 redis:alpine"
    echo "   - macOS: brew services start redis"
    echo "   - Linux: sudo systemctl start redis"
    echo ""
    exit 1
fi

echo "✅ Redis está rodando"
echo ""

# Verificar se .env existe no backend
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "   Copie env.example.txt para .env e configure:"
    echo "   cd backend && cp env.example.txt .env"
    echo "   Edite o .env com suas credenciais"
    echo ""
    exit 1
fi

echo "✅ Arquivo .env encontrado"
echo ""

# Iniciar Celery em background
echo "📦 Iniciando Celery worker..."
cd backend
celery -A app.tasks.celery_app worker --loglevel=info &
CELERY_PID=$!
cd ..

sleep 2

# Iniciar FastAPI
echo "🌐 Iniciando servidor FastAPI..."
cd backend
uvicorn app.main:app --reload --port 8000 &
FASTAPI_PID=$!
cd ..

sleep 3

# Iniciar Frontend
echo "⚛️  Iniciando frontend React..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Sistema iniciado!"
echo ""
echo "📊 Serviços rodando:"
echo "   - Celery Worker: PID $CELERY_PID"
echo "   - FastAPI: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo ""
echo "📝 Para parar todos os serviços, execute:"
echo "   kill $CELERY_PID $FASTAPI_PID $FRONTEND_PID"
echo ""
echo "🌐 Acesse: http://localhost:3000"

# Aguardar Ctrl+C
wait






