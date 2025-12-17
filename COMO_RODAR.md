# 🚀 Como Rodar o Sistema - Guia Completo

## ✅ Pré-requisitos

### 1. Python 3.9+
```bash
python3 --version  # Deve ser 3.9 ou superior
```

### 2. Node.js e npm
```bash
node --version
npm --version
```

### 3. Tesseract OCR (OBRIGATÓRIO para OCR)
```bash
# macOS
brew install tesseract
brew install tesseract-lang  # Para suporte a português

# Verificar instalação
tesseract --version
tesseract --list-langs  # Deve incluir 'por' para português
```

> ⚠️ **Nota:** Se o Tesseract não estiver instalado, o sistema funcionará, mas sem OCR (extrai apenas texto selecionável do PDF).

### 4. PostgreSQL e Redis
- ✅ PostgreSQL configurado remotamente
- ✅ Redis configurado remotamente
- As URLs estão no arquivo `.env`

## 🚀 Instalação e Configuração

### 1️⃣ Configurar Backend

```bash
cd backend

# Criar ambiente virtual (se ainda não criou)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação das novas dependências
pip list | grep -E "pytesseract|imagehash"
```

**Dependências principais:**
- `pytesseract==0.3.10` - OCR para extrair texto de imagens
- `imagehash==4.3.1` - Detecção de imagens duplicadas
- `fastapi`, `celery`, `sqlalchemy`, etc.

### 2️⃣ Configurar Arquivo .env

```bash
cd backend

# Se não existir, copie:
cp env.example.txt .env

# O .env já está preenchido com:
# - PostgreSQL (remoto)
# - Redis (remoto)
# - Gemini API Key
# - OpenAI API Key
```

### 3️⃣ Configurar Banco de Dados

**Execute o schema no PostgreSQL:**
```sql
-- Arquivo: postgres_schema.sql
-- Execute no seu cliente PostgreSQL

-- Se já tinha o banco, adicione apenas os novos campos:
ALTER TABLE imagens ADD COLUMN IF NOT EXISTS hash_imagem VARCHAR(64);
ALTER TABLE imagens ADD COLUMN IF NOT EXISTS perceptual_hash VARCHAR(32);
CREATE INDEX IF NOT EXISTS idx_imagens_hash ON imagens(hash_imagem);
```

**Inicializar banco (opcional):**
```bash
cd backend
source venv/bin/activate
python3 -c "from app.services.database import init_db; init_db(); print('✅ Banco inicializado')"
```

### 4️⃣ Configurar Frontend

```bash
cd frontend

# Instalar dependências
npm install
```

## 🎯 Executar o Sistema

### Terminal 1 - Celery Worker (Processamento de PDFs)

```bash
cd backend
source venv/bin/activate
celery -A app.tasks worker --loglevel=info --pool=solo
```

> ⚠️ **IMPORTANTE:** `--pool=solo` é **obrigatório** no macOS para evitar erros SIGSEGV.

**O que faz:**
- Processa PDFs de forma assíncrona
- Extrai questões e imagens
- Usa OCR, IA e múltiplas estratégias

### Terminal 2 - FastAPI (API Backend)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**URLs:**
- API: http://localhost:8000
- Documentação: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/provas

### Terminal 3 - Frontend (Interface Web)

```bash
cd frontend
npm run dev
```

**URL:**
- Interface: http://localhost:3000

## 🆕 Novas Funcionalidades

### 1. OCR (Tesseract)
- Extrai texto de imagens do PDF
- Suporta português e inglês
- Combina texto do PDF + texto do OCR

### 2. Deduplicação de Imagens
- **Hash MD5:** Detecta duplicatas exatas
- **Perceptual Hash:** Detecta similaridade visual (95%+)
- **Filtros:** Remove imagens muito pequenas (<50px)
- **Filtros de posição:** Remove imagens de cabeçalho/rodapé

### 3. Múltiplas Estratégias de Extração
- **Regex aprimorado:** Múltiplos padrões (1., 1), Questão 1, Q.1, etc.)
- **Processamento por página:** Melhor contexto e rastreamento
- **IA por chunks:** ChatGPT processa em grupos menores
- **Validação:** ChatGPT valida e refina extrações

### 4. Prompts Melhorados
- Específicos para provas de concursos
- Exemplos detalhados
- Processamento em chunks menores

## 🧪 Testar o Sistema

1. **Acesse:** http://localhost:3000
2. **Faça upload** de um PDF de prova
3. **Acompanhe o processamento:**
   - Status no frontend
   - Logs no terminal do Celery
4. **Quando concluído:**
   - Expanda a prova para ver questões
   - Veja imagens associadas às questões

## 🐛 Problemas Comuns e Soluções

### Erro: "tesseract not found"
```bash
# Instalar Tesseract
brew install tesseract tesseract-lang  # macOS
# ou
sudo apt-get install tesseract-ocr tesseract-ocr-por  # Linux

# Verificar
tesseract --version
```

### Erro: "ModuleNotFoundError: pytesseract"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "column hash_imagem does not exist"
```sql
-- Execute no PostgreSQL:
ALTER TABLE imagens ADD COLUMN IF NOT EXISTS hash_imagem VARCHAR(64);
ALTER TABLE imagens ADD COLUMN IF NOT EXISTS perceptual_hash VARCHAR(32);
CREATE INDEX IF NOT EXISTS idx_imagens_hash ON imagens(hash_imagem);
```

### Erro: "WorkerLostError: SIGSEGV"
```bash
# Use --pool=solo no macOS (já incluído nos comandos acima)
celery -A app.tasks worker --loglevel=info --pool=solo
```

### Erro: "SyntaxError: invalid syntax"
- ✅ **Já corrigido!** O erro estava em `ai_analyzer.py` e foi resolvido.

### Erro: "Redis connection refused"
- Redis está configurado remotamente
- Verifique a URL no `.env`
- Teste: `redis-cli -h [HOST] -p [PORT] -a [PASSWORD] ping`

### Erro: "PostgreSQL connection failed"
- Verifique a URL no `.env`
- Teste a conexão manualmente
- Verifique se o servidor está acessível

### Frontend não conecta ao backend
- Verifique se FastAPI está rodando na porta 8000
- Verifique o proxy no `vite.config.ts`
- Teste: `curl http://localhost:8000/api/provas`

## 📊 Verificar Status dos Serviços

```bash
# Ver processos rodando
ps aux | grep -E "celery|uvicorn|vite" | grep -v grep

# Testar API
curl http://localhost:8000/api/provas

# Testar Frontend
curl http://localhost:3000

# Ver logs do Celery
# (aparecem no terminal onde foi iniciado)
```

## 🛑 Parar Serviços

```bash
# Parar todos os serviços
pkill -f "celery.*worker"
pkill -f "uvicorn.*app.main"
pkill -f "vite"

# Ou parar individualmente (Ctrl+C nos terminais)
```

## 🔄 Reiniciar Serviços

1. Pare os serviços (comandos acima)
2. Execute novamente os comandos de inicialização
3. Aguarde alguns segundos para inicialização completa

## 📝 Estrutura do Projeto

```
AnalizePDF/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── ocr_service.py          # ✨ NOVO: OCR
│   │   │   ├── image_deduplicator.py   # ✨ NOVO: Deduplicação
│   │   │   ├── question_extractor.py   # ✨ NOVO: Extração por página
│   │   │   ├── ai_analyzer.py          # 🔧 MELHORADO: Prompts
│   │   │   ├── pdf_extractor.py        # 🔧 MELHORADO: Regex
│   │   │   └── image_processor.py       # 🔧 MELHORADO: Hash
│   │   ├── tasks/
│   │   │   └── process_pdf.py          # 🔧 MELHORADO: Pipeline completo
│   │   └── ...
│   ├── requirements.txt                # 🔧 ATUALIZADO: pytesseract, imagehash
│   └── .env
├── frontend/
│   └── ...
├── postgres_schema.sql                  # 🔧 ATUALIZADO: Campos hash
└── COMO_RODAR.md                        # 📖 Este arquivo
```

## ✅ Checklist de Inicialização

- [ ] Python 3.9+ instalado
- [ ] Node.js e npm instalados
- [ ] Tesseract OCR instalado e configurado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências Python instaladas (`pip install -r requirements.txt`)
- [ ] Dependências Node instaladas (`npm install`)
- [ ] Arquivo `.env` configurado
- [ ] Banco de dados PostgreSQL configurado (schema executado)
- [ ] Celery Worker rodando (Terminal 1)
- [ ] FastAPI rodando (Terminal 2)
- [ ] Frontend rodando (Terminal 3)
- [ ] Teste de acesso: http://localhost:3000

## 🎉 Pronto!

Agora você pode:
- ✅ Fazer upload de PDFs de provas
- ✅ Extrair questões automaticamente
- ✅ Extrair e associar imagens
- ✅ Usar OCR para texto em imagens
- ✅ Remover duplicatas automaticamente
- ✅ Acessar tudo via interface web

**Boa sorte com suas provas! 🚀**
