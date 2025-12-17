# 🍎 Comandos para macOS

No macOS, use `python3` em vez de `python`.

## 🚀 Passo a Passo para Rodar

### 1. Criar e Ativar Ambiente Virtual (Backend)

```bash
cd /Volumes/HD/Codigos/AnalizePDF/backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências (Backend)

```bash
pip install -r requirements.txt
```

### 3. Rodar os 3 Serviços

**Terminal 1 - Celery Worker:**
```bash
cd /Volumes/HD/Codigos/AnalizePDF/backend
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 2 - FastAPI:**
```bash
cd /Volumes/HD/Codigos/AnalizePDF/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 - Frontend:**
```bash
cd /Volumes/HD/Codigos/AnalizePDF/frontend
npm install  # só na primeira vez
npm run dev
```

## ✅ Pronto!

Acesse: **http://localhost:3000**

---

## 💡 Dica

Se você sempre usar `python3`, pode criar um alias no seu `~/.zshrc`:

```bash
echo 'alias python=python3' >> ~/.zshrc
source ~/.zshrc
```

Assim você pode usar `python` normalmente.






