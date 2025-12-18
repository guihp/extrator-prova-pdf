# 🚀 Guia de Deploy - Coolify

Este documento descreve como fazer deploy do projeto no Coolify.

## 📋 Pré-requisitos

- Conta no Coolify configurada
- Repositório GitHub com o código
- Banco PostgreSQL acessível
- Redis acessível (pode ser no próprio Coolify ou externo)

## 🔧 Configuração no Coolify

### 1. Variáveis de Ambiente

Configure as seguintes variáveis de ambiente no Coolify para o **Backend**:

```env
# PostgreSQL
POSTGRES_URL=postgresql://usuario:senha@host:porta/database

# APIs
GEMINI_API_KEY=sua_chave_gemini
OPENAI_API_KEY=sua_chave_openai

# Redis
REDIS_URL=redis://usuario:senha@host:porta/0

# Configurações
UPLOAD_DIR=uploads
IMAGES_DIR=images
MAX_FILE_SIZE=10485760
BASE_URL=https://api.seudominio.com
```

Configure as seguintes variáveis de ambiente para o **Frontend**:

```env
VITE_API_BASE_URL=https://api.seudominio.com
```

### 2. Serviços Necessários

#### Backend (FastAPI + Celery)

**Serviço 1: FastAPI (Backend)**
- **Porta**: 8000
- **Comando de Build**: (se usar Docker, configure o Dockerfile)
- **Comando de Inicialização**: 
  ```bash
  cd backend && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
- **Health Check**: `/health`

**Serviço 2: Celery Worker**
- **Comando de Inicialização**:
  ```bash
  cd backend && celery -A app.tasks.celery_app worker --loglevel=info
  ```
- ⚠️ **Importante**: Celery precisa das mesmas variáveis de ambiente do backend

#### Frontend (React + Vite)

**Serviço: Frontend**
- **Porta**: 3000 (ou a que você configurar)
- **Comando de Build**: 
  ```bash
  cd frontend && npm install && npm run build
  ```
- **Comando de Inicialização**:
  ```bash
  cd frontend && npm run preview
  ```
- **Ou usar nginx**: Servir a pasta `frontend/dist` com nginx

### 3. Banco de Dados

Execute o script SQL no PostgreSQL antes de iniciar:

```bash
# Execute o arquivo postgres_schema.sql e ADICIONAR_COLUNA_FORMATADO.sql
```

Ou deixe o sistema criar automaticamente (a primeira vez que rodar, o FastAPI criará as tabelas).

### 4. Estrutura de Diretórios

Certifique-se de que os diretórios existam no servidor:

```bash
backend/uploads/
backend/images/
```

Ou configure no Coolify para criar esses diretórios.

## 🐳 Docker (Opcional)

Se preferir usar Docker, você pode criar os seguintes arquivos:

### backend/Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml (para desenvolvimento local)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - backend/.env
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/images:/app/images

  celery:
    build: ./backend
    command: celery -A app.tasks.celery_app worker --loglevel=info
    env_file:
      - backend/.env
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/images:/app/images

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
```

## ✅ Checklist de Deploy

- [ ] Variáveis de ambiente configuradas no Coolify
- [ ] Banco de dados PostgreSQL acessível e schema executado
- [ ] Redis acessível
- [ ] Backend (FastAPI) rodando e respondendo em `/health`
- [ ] Celery Worker rodando
- [ ] Frontend buildado e servindo
- [ ] Frontend configurado com URL correta da API
- [ ] Diretórios `uploads/` e `images/` criados e com permissões corretas
- [ ] Testado upload de PDF
- [ ] Testado visualização de questões formatadas

## 🔍 Troubleshooting

### Backend não conecta ao banco
- Verifique se `POSTGRES_URL` está correto
- Verifique se o banco aceita conexões do servidor do Coolify

### Celery não processa tarefas
- Verifique se o Redis está acessível
- Verifique se `REDIS_URL` está correto
- Verifique os logs do Celery

### Frontend não carrega dados
- Verifique se `VITE_API_BASE_URL` está apontando para o backend correto
- Verifique CORS no backend (já está configurado para `allow_origins=["*"]`)
- Verifique se o backend está respondendo

### Imagens não aparecem
- Verifique se o diretório `images/` existe
- Verifique se `BASE_URL` está correto
- Verifique permissões de leitura dos arquivos

## 📝 Notas

- O backend precisa rodar na porta 8000 (ou a que você configurar)
- O Celery precisa rodar como um serviço separado
- O frontend pode ser servido como SPA (Single Page Application) usando nginx ou similar
- Considere usar volumes persistentes para `uploads/` e `images/` no Coolify

## ⚠️ Importante: Configuração do docker-compose.yml

**NÃO mapeie portas no docker-compose.yml quando usando Coolify!**

O Coolify gerencia networking e portas automaticamente através dos domínios configurados. Mapeamentos de porta explícitos (como `ports: - "8000:8000"`) causam conflitos e erros como "port is already allocated".

### Configuração Correta

Use `expose` em vez de `ports`:

```yaml
services:
  backend:
    expose:
      - "8000"  # Expor apenas internamente, Coolify gerencia o roteamento
      
  frontend:
    expose:
      - "80"  # Nginx roda na porta 80
```

O Coolify detecta automaticamente as portas através dos labels `coolify.managed=true` e roteia o tráfego através dos domínios configurados (ex: `api.flowera.com.br` e `app.flowera.com.br`).

