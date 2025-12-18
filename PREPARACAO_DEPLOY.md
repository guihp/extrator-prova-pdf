# ✅ Preparação para Deploy - Checklist

## 🔒 Segurança - CORRIGIDO

- [x] Removidas credenciais reais do `env.example.txt`
- [x] Removido arquivo `VARIAVEIS_AMBIENTE.txt` com credenciais
- [x] Removida URL hardcoded do Redis no `config.py`
- [x] Atualizado `.gitignore` para ignorar arquivos `.env` do frontend
- [x] Frontend configurado para usar variável de ambiente `VITE_API_BASE_URL`

## 📝 Arquivos Modificados para Deploy

### Backend
- ✅ `backend/env.example.txt` - Limpo, sem credenciais reais
- ✅ `backend/app/config.py` - Redis URL removida (usa variável de ambiente)

### Frontend
- ✅ `frontend/src/services/api.ts` - Usa `VITE_API_BASE_URL` da variável de ambiente
- ✅ `.gitignore` - Atualizado para ignorar `.env` do frontend

### Documentação
- ✅ `DEPLOY.md` - Guia completo de deploy para Coolify
- ✅ `PREPARACAO_DEPLOY.md` - Este arquivo

## 🚀 Próximos Passos

### 1. No GitHub

```bash
# Verificar status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "Preparação para deploy: removidas credenciais e adicionada documentação"

# Push
git push origin main
```

### 2. No Coolify

1. **Criar projeto** conectado ao repositório GitHub
2. **Configurar variáveis de ambiente** (veja `DEPLOY.md`)
3. **Configurar serviços**:
   - Backend (FastAPI) - porta 8000
   - Celery Worker
   - Frontend (React)

### 3. Variáveis de Ambiente no Coolify

**Backend:**
```
POSTGRES_URL=postgresql://...
GEMINI_API_KEY=...
OPENAI_API_KEY=...
REDIS_URL=redis://...
BASE_URL=https://api.seudominio.com
```

**Frontend:**
```
VITE_API_BASE_URL=https://api.seudominio.com
```

### 4. Executar Scripts SQL

Execute no PostgreSQL antes de iniciar:
- `postgres_schema.sql`
- `ADICIONAR_COLUNA_FORMATADO.sql`

## ⚠️ Importante

- ✅ Não commite arquivos `.env` com credenciais reais
- ✅ Use variáveis de ambiente no Coolify para todas as credenciais
- ✅ Certifique-se de que `BASE_URL` no backend aponte para a URL de produção
- ✅ Certifique-se de que `VITE_API_BASE_URL` no frontend aponte para a URL da API

## ✅ Status

**O projeto está pronto para deploy no Coolify!**

Todas as credenciais foram removidas do código e a documentação de deploy foi criada.

