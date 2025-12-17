# 🛑 Como Parar os Serviços

## ⚠️ Problema: Ctrl+C não funciona

Se o Celery worker não está encerrando com `Ctrl+C`, use os métodos abaixo.

## 🔧 Métodos para Parar

### Método 1: Pelo Terminal (Recomendado)

**Se estiver no terminal onde o serviço está rodando:**
```bash
# Pressione Ctrl+C uma vez e aguarde
# Se não funcionar, pressione Ctrl+C novamente
# Ou use Ctrl+Z para suspender e depois mate o processo
```

### Método 2: Matar Processo por PID

```bash
# 1. Encontrar o PID
ps aux | grep "celery.*worker" | grep -v grep

# 2. Matar o processo (substitua PID pelo número encontrado)
kill -9 <PID>

# Ou em um comando só:
pkill -9 -f "celery.*worker"
```

### Método 3: Matar Todos os Serviços

```bash
# Parar Celery
pkill -9 -f "celery.*worker"

# Parar FastAPI
pkill -9 -f "uvicorn.*app.main"

# Parar Frontend
pkill -9 -f "vite"

# Verificar se parou
ps aux | grep -E "celery|uvicorn|vite" | grep -v grep
```

### Método 4: Usar lsof (Localizar e Matar)

```bash
# Encontrar processo usando a porta (se aplicável)
lsof -ti:8000 | xargs kill -9  # FastAPI
lsof -ti:3000 | xargs kill -9  # Frontend

# Celery não usa porta específica, use pkill
pkill -9 -f "celery.*worker"
```

## 🔍 Verificar se Parou

```bash
# Ver todos os processos relacionados
ps aux | grep -E "celery|uvicorn|vite" | grep -v grep

# Se não retornar nada, todos os serviços pararam ✅
```

## ⚡ Comando Rápido (Tudo de Uma Vez)

```bash
# Parar tudo
pkill -9 -f "celery.*worker"; pkill -9 -f "uvicorn.*app.main"; pkill -9 -f "vite"

# Verificar
ps aux | grep -E "celery|uvicorn|vite" | grep -v grep || echo "✅ Todos os serviços parados"
```

## 🚨 Por que Ctrl+C não funciona?

1. **Celery pode estar processando uma tarefa longa**
   - Aguarde a tarefa terminar
   - Ou force com `kill -9`

2. **Processo pode estar travado**
   - Use `kill -9` para forçar encerramento

3. **Múltiplos processos**
   - Verifique se há vários processos rodando
   - Mate todos com `pkill`

## 💡 Dica: Criar Script de Parada

Crie um arquivo `stop.sh`:

```bash
#!/bin/bash

echo "🛑 Parando serviços..."

# Parar Celery
pkill -9 -f "celery.*worker" && echo "✅ Celery parado" || echo "⚠️ Celery não estava rodando"

# Parar FastAPI
pkill -9 -f "uvicorn.*app.main" && echo "✅ FastAPI parado" || echo "⚠️ FastAPI não estava rodando"

# Parar Frontend
pkill -9 -f "vite" && echo "✅ Frontend parado" || echo "⚠️ Frontend não estava rodando"

echo ""
echo "📊 Verificando processos restantes..."
ps aux | grep -E "celery|uvicorn|vite" | grep -v grep || echo "✅ Nenhum processo encontrado"
```

Tornar executável:
```bash
chmod +x stop.sh
./stop.sh
```

## 🔄 Reiniciar Após Parar

```bash
# Terminal 1 - Celery
cd backend && source venv/bin/activate && celery -A app.tasks worker --loglevel=info --pool=solo

# Terminal 2 - FastAPI
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm run dev
```




