# 🔍 Como Verificar e Gerenciar Serviços

## ✅ Verificar Status dos Serviços

### Método Rápido
```bash
# Ver todos os processos rodando
ps aux | grep -E "celery|uvicorn|vite" | grep -v grep
```

### Verificar Individualmente

**1. Celery Worker:**
```bash
ps aux | grep "celery.*worker" | grep -v grep
# Se aparecer algo, está rodando ✅
```

**2. FastAPI:**
```bash
# Ver processo
ps aux | grep "uvicorn.*app.main" | grep -v grep

# Testar API
curl http://localhost:8000/api/provas
# Se retornar JSON ou lista vazia, está funcionando ✅
```

**3. Frontend:**
```bash
# Ver processo
ps aux | grep "vite" | grep -v grep

# Testar frontend
curl http://localhost:3000
# Se retornar HTML, está funcionando ✅
```

## ⚠️ Erro: "Address already in use"

Se você ver este erro:
```
ERROR: [Errno 48] Address already in use
```

**Significa que o serviço já está rodando!** ✅

### Verificar se está funcionando:
```bash
# FastAPI
curl http://localhost:8000/api/provas

# Frontend
curl http://localhost:3000
```

Se estiver respondendo, **não precisa iniciar novamente!**

## 🛑 Parar Serviços

### Parar Todos
```bash
pkill -f "celery.*worker"
pkill -f "uvicorn.*app.main"
pkill -f "vite"
```

### Parar Individualmente

**1. Parar Celery:**
```bash
pkill -f "celery.*worker"
# ou encontrar PID e matar:
lsof -ti:6379  # Redis (se local)
ps aux | grep celery | grep -v grep | awk '{print $2}' | xargs kill
```

**2. Parar FastAPI:**
```bash
pkill -f "uvicorn.*app.main"
# ou
lsof -ti:8000 | xargs kill
```

**3. Parar Frontend:**
```bash
pkill -f "vite"
# ou
lsof -ti:3000 | xargs kill
```

## 🔄 Reiniciar Serviços

### Se quiser reiniciar tudo:
```bash
# 1. Parar todos
pkill -f "celery.*worker"
pkill -f "uvicorn.*app.main"
pkill -f "vite"

# 2. Aguardar 2 segundos
sleep 2

# 3. Reiniciar (em terminais separados)
# Terminal 1:
cd backend && source venv/bin/activate && celery -A app.tasks worker --loglevel=info --pool=solo

# Terminal 2:
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 3:
cd frontend && npm run dev
```

## 📊 Ver Portas em Uso

```bash
# Ver qual processo usa a porta 8000
lsof -ti:8000

# Ver qual processo usa a porta 3000
lsof -ti:3000

# Ver todas as portas em uso
lsof -i -P | grep LISTEN
```

## 🎯 Script de Verificação Completa

Crie um arquivo `verificar.sh`:
```bash
#!/bin/bash

echo "=== STATUS DOS SERVIÇOS ==="
echo ""

echo "1. Celery Worker:"
if ps aux | grep "celery.*worker" | grep -v grep > /dev/null; then
    echo "   ✅ Rodando"
    ps aux | grep "celery.*worker" | grep -v grep | awk '{print "   PID: " $2}'
else
    echo "   ❌ Não está rodando"
fi

echo ""
echo "2. FastAPI:"
if ps aux | grep "uvicorn.*app.main" | grep -v grep > /dev/null; then
    echo "   ✅ Rodando"
    ps aux | grep "uvicorn.*app.main" | grep -v grep | awk '{print "   PID: " $2}'
    if curl -s http://localhost:8000/api/provas > /dev/null; then
        echo "   ✅ API respondendo"
    else
        echo "   ⚠️ API não respondendo"
    fi
else
    echo "   ❌ Não está rodando"
fi

echo ""
echo "3. Frontend:"
if ps aux | grep "vite" | grep -v grep > /dev/null; then
    echo "   ✅ Rodando"
    ps aux | grep "vite" | grep -v grep | awk '{print "   PID: " $2}'
    if curl -s http://localhost:3000 > /dev/null; then
        echo "   ✅ Frontend respondendo"
    else
        echo "   ⚠️ Frontend não respondendo"
    fi
else
    echo "   ❌ Não está rodando"
fi

echo ""
echo "=== URLs ==="
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
```

Tornar executável:
```bash
chmod +x verificar.sh
./verificar.sh
```

## 💡 Dicas

1. **Se o serviço já está rodando, não precisa iniciar novamente!**
2. **Use `--reload` no uvicorn para recarregar automaticamente ao salvar arquivos**
3. **Os logs aparecem nos terminais onde os serviços foram iniciados**
4. **No macOS, sempre use `--pool=solo` no Celery**




