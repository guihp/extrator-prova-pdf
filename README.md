# Sistema de Análise de PDFs de Provas

Sistema completo para análise automática de PDFs de provas, extração de questões numeradas e imagens associadas, utilizando Google Gemini e OpenAI ChatGPT para análise inteligente.

## 🚀 Funcionalidades

- ✅ Upload de PDFs via interface web
- ✅ Extração automática de questões numeradas (1, 2, 3...)
- ✅ Extração de todas as imagens do PDF
- ✅ Mapeamento inteligente de imagens às questões usando IA
- ✅ Análise com Google Gemini (estrutura) e ChatGPT (validação)
- ✅ Armazenamento no Supabase (PostgreSQL + Storage)
- ✅ Processamento assíncrono com Celery
- ✅ Interface web React com TypeScript

## 📋 Pré-requisitos

- Python 3.9+
- Node.js 18+
- Redis (para Celery)
- Conta Supabase
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

## 🗄️ Configuração do Supabase

1. Crie um projeto no Supabase
2. Execute o script SQL em `supabase_schema.sql` no SQL Editor
3. Crie um bucket de storage chamado `provas-images` (ou ajuste no código)
4. Configure as políticas de acesso conforme necessário

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
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Redis
REDIS_URL=redis://localhost:6379/0
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
- As imagens são armazenadas no Supabase Storage com URLs públicas
- Cada questão mantém referência às suas imagens associadas

## 🐛 Troubleshooting

- Certifique-se de que o Redis está rodando antes de iniciar o Celery
- Verifique as variáveis de ambiente no arquivo `.env`
- Confirme que o bucket do Supabase Storage foi criado
- Verifique os logs do Celery para erros de processamento

