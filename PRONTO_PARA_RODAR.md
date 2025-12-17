# 🚀 PRONTO PARA RODAR!

Todas as configurações já estão prontas! Você só precisa:

## ✅ 1. Verificar/Criar arquivo .env

```bash
cd backend
cp env.example.txt .env
```

O arquivo `.env` já terá todas as configurações:
- ✅ PostgreSQL (URL pública configurada)
- ✅ Redis (URL pública configurada)
- ✅ Gemini API Key
- ✅ OpenAI API Key

## ✅ 2. Executar Schema SQL (Opcional)

O sistema pode criar as tabelas automaticamente, mas se quiser executar manualmente:

```bash
# Execute o arquivo postgres_schema.sql no seu banco PostgreSQL
# Ou deixe o sistema criar automaticamente na primeira execução
```

## 🚀 3. Rodar os 3 Serviços

### Terminal 1 - Celery Worker:
```bash
cd /Volumes/HD/Codigos/AnalizePDF/backend
python3 -m venv venv  # só na primeira vez (já criado!)
source venv/bin/activate
pip install -r requirements.txt  # já instalado!
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

## 🎉 4. Acessar

Abra: **http://localhost:3000**

Faça upload de um PDF e veja funcionando! 🎊

---

## ⚠️ Importante

- As chaves de API estão no `env.example.txt` - certifique-se de que o `.env` foi criado
- O `.env` está no `.gitignore` para não ser commitado
- Se as tabelas não existirem, o sistema criará automaticamente na primeira execução

