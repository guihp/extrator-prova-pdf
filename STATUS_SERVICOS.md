# 🚀 Status dos Serviços

## ✅ Serviços Iniciados

### 1. Celery Worker
- **Status:** ✅ Rodando em background
- **Comando:** `celery -A app.tasks worker --loglevel=info --pool=solo`
- **Função:** Processa PDFs de forma assíncrona
- **Pool:** `solo` (necessário no macOS)

### 2. FastAPI Backend
- **Status:** ✅ Rodando em background
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Função:** API REST para upload e consulta

### 3. Frontend React
- **Status:** ✅ Rodando em background
- **URL:** http://localhost:3000
- **Função:** Interface web para upload de provas

## 📋 Verificação Rápida

```bash
# Verificar FastAPI
curl http://localhost:8000/api/provas

# Verificar Frontend
curl http://localhost:3000

# Ver processos rodando
ps aux | grep -E "celery|uvicorn|vite" | grep -v grep
```

## 🛑 Parar Serviços

```bash
# Encontrar e matar processos
pkill -f "celery.*worker"
pkill -f "uvicorn.*app.main"
pkill -f "vite"
```

## 📝 Logs

Os logs aparecem nos terminais onde os serviços foram iniciados.

Para ver logs em tempo real:
```bash
# Celery
tail -f /tmp/celery.log  # se houver arquivo de log

# FastAPI
# Logs aparecem no terminal onde foi iniciado
```

## 🔄 Reiniciar

Se precisar reiniciar:
1. Pare os serviços (comandos acima)
2. Execute novamente os comandos de inicialização




