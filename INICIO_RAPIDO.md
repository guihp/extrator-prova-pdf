# ⚡ Início Rápido - Rodar o Sistema AGORA

## 🔴 ANTES DE TUDO - Configure estas 3 coisas:

### 1. Redis (Já configurado! ✅)
A URL pública do Redis já está configurada no código:
```
redis://default:BW8XH6cfzwX7oPpc0HOiBDHg56WtAxqJg6sChzbw2a3dzFdhbsLOVbQJSivzMJtv@72.60.146.143:5433/0
```

### 2. Arquivo .env no Backend (Obrigatório)
```bash
cd backend
cp env.example.txt .env
```

**Edite o arquivo `.env` e coloque suas credenciais:**
```env
# PostgreSQL (URL completa - já configurada!)
POSTGRES_URL=postgres://postgres:DvMaicTTXDkVL6r5YReP9sQX0ihs8W7DGbkWJhbsoh0BDdKhdsTQCWQUz2o2CA7F@72.60.146.143:5435/postgres

# Google Gemini
GEMINI_API_KEY=sua_gemini_key

# OpenAI
OPENAI_API_KEY=sua_openai_key

# Redis (já configurado!)
REDIS_URL=redis://default:BW8XH6cfzwX7oPpc0HOiBDHg56WtAxqJg6sChzbw2a3dzFdhbsLOVbQJSivzMJtv@72.60.146.143:5433/0

# Configurações
BASE_URL=http://localhost:8000
```

### 3. PostgreSQL (Já configurado! ✅)
A URL pública do PostgreSQL já está configurada no `env.example.txt`:
```
postgres://postgres:DvMaicTTXDkVL6r5YReP9sQX0ihs8W7DGbkWJhbsoh0BDdKhdsTQCWQUz2o2CA7F@72.60.146.143:5435/postgres
```

**Importante:** Execute o script `postgres_schema.sql` no seu banco PostgreSQL ou deixe o sistema criar as tabelas automaticamente na primeira execução.

---

## 🚀 AGORA RODE (3 Terminais):

### Terminal 1 - Celery Worker:
```bash
cd /Volumes/HD/Codigos/AnalizePDF/backend
python -m venv venv  # só na primeira vez
source venv/bin/activate
pip install -r requirements.txt  # só na primeira vez
celery -A app.tasks.celery_app worker --loglevel=info
```

### Terminal 2 - FastAPI:
```bash
cd /Volumes/HD/Codigos/AnalizePDF/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 3 - Frontend:
```bash
cd /Volumes/HD/Codigos/AnalizePDF/frontend
npm install  # só na primeira vez
npm run dev
```

---

## ✅ PRONTO!

Abra: **http://localhost:3000**

Faça upload de um PDF e veja a mágica acontecer! 🎉

**Nota:** As imagens serão salvas localmente na pasta `backend/images/` e servidas via FastAPI.

---

## 🐛 Se der erro:

**"Redis connection refused"**
→ Verifique se a URL do Redis está correta no `.env`

**"PostgreSQL connection failed"**
→ Verifique as credenciais do PostgreSQL no `.env`
→ Certifique-se de que o banco existe e o schema foi executado

**"Module not found"**
→ Execute: `pip install -r requirements.txt` no backend

**"Invalid API key"**
→ Verifique o arquivo `.env` no backend

**"Table does not exist"**
→ Execute o `postgres_schema.sql` ou deixe o sistema criar automaticamente
