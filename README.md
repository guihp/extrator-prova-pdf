# Sistema de Análise de PDFs de Provas

Sistema completo para análise automática de PDFs de provas, extração de questões numeradas e imagens associadas, utilizando Google Gemini e OpenAI ChatGPT para análise inteligente.

## 🚀 Funcionalidades

- ✅ Upload de PDFs via interface web
- ✅ Extração automática de questões numeradas (1, 2, 3...)
- ✅ Extração de todas as imagens do PDF
- ✅ Mapeamento inteligente de imagens às questões usando IA
- ✅ Análise com Google Gemini (estrutura) e ChatGPT (validação)
- ✅ OCR com Tesseract para extrair texto de imagens
- ✅ Deduplicação inteligente de imagens (hash MD5 e perceptual hash)
- ✅ Armazenamento em PostgreSQL
- ✅ Processamento assíncrono com Celery
- ✅ Interface web React com TypeScript
- ✅ Pronto para deploy no Coolify com Docker

## 📋 Pré-requisitos

- Python 3.9+
- Node.js 18+
- PostgreSQL (banco de dados)
- Redis (URL pública já configurada)
- API Keys: Google Gemini e OpenAI

## 🛠️ Instalação

### Backend

1. Entre na pasta do backend:
```bash
cd backend
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

### Frontend

1. Entre na pasta do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

## 🗄️ Configuração do PostgreSQL

1. Crie um banco de dados PostgreSQL
2. Execute o script SQL em `postgres_schema.sql` no seu banco
3. Ou deixe o sistema criar as tabelas automaticamente na primeira execução
4. Configure as credenciais no arquivo `.env`

## 🚀 Executando

### Backend

1. Inicie o Redis:
```bash
redis-server
```

2. Inicie o worker Celery (em um terminal):
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

3. Inicie o servidor FastAPI (em outro terminal):
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

## 📁 Estrutura do Projeto

```
AnalizePDF/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configurações
│   │   ├── models/              # Modelos Pydantic
│   │   ├── routes/              # Endpoints da API
│   │   ├── services/            # Serviços (PDF, IA, Supabase)
│   │   └── tasks/               # Tarefas Celery
│   └── requirements.txt
├── frontend/
│   └── src/                     # Código React
├── supabase_schema.sql          # Schema do banco
└── README.md
```

## 🔧 Variáveis de Ambiente

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=analize_pdf

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Redis (URL pública já configurada)
REDIS_URL=redis://default:BW8XH6cfzwX7oPpc0HOiBDHg56WtAxqJg6sChzbw2a3dzFdhbsLOVbQJSivzMJtv@72.60.146.143:5433/0

# Configurações
BASE_URL=http://localhost:8000
```

## 📡 API Endpoints

- `POST /provas/upload` - Upload de PDF
- `GET /provas/` - Listar todas as provas
- `GET /provas/{id}` - Buscar prova completa
- `GET /provas/{id}/questoes` - Buscar questões de uma prova
- `GET /provas/{id}/imagens` - Buscar imagens de uma prova

## 🔄 Fluxo de Processamento

1. Upload do PDF via interface web
2. Validação e salvamento temporário
3. Criação de registro no banco (status: "processando")
4. Enfileiramento de tarefa Celery
5. Extração de texto e imagens
6. Análise com Gemini (identificação de questões)
7. Validação com ChatGPT
8. Mapeamento de imagens às questões
9. Upload de imagens para Supabase Storage
10. Atualização de status para "concluído"

## 📝 Notas

- O processamento é assíncrono, então o upload retorna imediatamente
- Use polling ou WebSockets para atualizar o status em tempo real
- As imagens são armazenadas localmente na pasta `backend/images/` e servidas via FastAPI
- Cada questão mantém referência às suas imagens associadas
- Redis público já está configurado, mas pode ser alterado no `.env`

## 🐳 Deploy com Docker

### Desenvolvimento Local

```bash
# Usar docker-compose
docker-compose up -d

# Ou build manual
docker build -t analize-pdf-backend ./backend
docker build -t analize-pdf-frontend ./frontend
```

### Deploy no Coolify

Veja o guia completo em [COOLIFY.md](./COOLIFY.md)

**Resumo rápido:**
1. Configure o repositório Git no Coolify
2. Use o `docker-compose.yml` ou configure serviços individuais
3. Configure as variáveis de ambiente
4. Configure volumes persistentes para `uploads/` e `images/`
5. Deploy!

## 🐛 Troubleshooting

- Certifique-se de que o Redis está rodando antes de iniciar o Celery
- Verifique as variáveis de ambiente no arquivo `.env`
- Confirme que o bucket do Supabase Storage foi criado
- Verifique os logs do Celery para erros de processamento
- No macOS, use `--pool=solo` no Celery para evitar erros SIGSEGV

## 📚 Documentação Adicional

- [COOLIFY.md](./COOLIFY.md) - Guia completo de deploy no Coolify
- [COMO_RODAR.md](./COMO_RODAR.md) - Instruções detalhadas de execução local

