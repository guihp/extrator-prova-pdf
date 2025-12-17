# ✅ Projeto Pronto para Deploy no Coolify

## 📋 Checklist de Arquivos Criados

Todos os arquivos necessários para deploy foram criados e configurados:

### Dockerfiles
- ✅ `backend/Dockerfile` - Backend FastAPI com Tesseract OCR
- ✅ `frontend/Dockerfile` - Frontend React com Nginx

### Configuração
- ✅ `docker-compose.yml` - Orquestração completa (3 serviços)
- ✅ `.dockerignore` - Arquivos ignorados no build
- ✅ `.gitignore` - Atualizado com arquivos sensíveis

### Documentação
- ✅ `COOLIFY.md` - Guia completo e detalhado
- ✅ `DEPLOY.md` - Guia rápido de deploy
- ✅ `README.md` - Atualizado com informações de deploy

### Scripts
- ✅ `backend/start.sh` - Script de inicialização (executável)

### Frontend
- ✅ `frontend/nginx.conf` - Configuração do Nginx
- ✅ `frontend/src/services/api.ts` - Atualizado para usar variáveis de ambiente
- ✅ `frontend/vite.config.ts` - Atualizado para proxy configurável

## 🚀 Próximos Passos

### 1. Commit e Push para GitHub

```bash
# Adicionar todos os arquivos
git add .

# Commit
git commit -m "Preparado para deploy no Coolify - Dockerfiles e configurações"

# Push para o repositório
git remote add origin https://github.com/guihp/extrator-prova-pdf.git
git branch -M main
git push -u origin main
```

### 2. Configurar no Coolify

Siga o guia em [DEPLOY.md](./DEPLOY.md) ou [COOLIFY.md](./COOLIFY.md)

### 3. Variáveis de Ambiente Necessárias

Configure estas variáveis no Coolify:

```
POSTGRES_URL=postgresql://user:password@host:port/database
GEMINI_API_KEY=sua_chave_gemini
OPENAI_API_KEY=sua_chave_openai
REDIS_URL=redis://user:password@host:port/0
BASE_URL=https://api.seudominio.com
VITE_API_URL=https://api.seudominio.com
```

### 4. Volumes Persistentes

Configure estes volumes no Coolify:

- `./backend/uploads` → `/app/uploads`
- `./backend/images` → `/app/images`

## 📦 Estrutura de Serviços

O projeto consiste em 3 serviços:

1. **backend** - FastAPI na porta 8000
2. **celery** - Worker Celery para processamento assíncrono
3. **frontend** - React/Vite com Nginx na porta 80

## 🔧 Configurações Importantes

### Backend
- Porta: `8000`
- Health check: `/health`
- API docs: `/docs`

### Frontend
- Porta: `80` (Nginx)
- Health check: `/health`
- Variável de ambiente: `VITE_API_URL` (usada no build)

### Celery
- Pool: `solo` (recomendado para evitar SIGSEGV)
- Log level: `info`

## ✅ Testes Locais (Opcional)

Antes de fazer deploy, você pode testar localmente:

```bash
# Build das imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## 🎯 Deploy no Coolify

### Opção Recomendada: Docker Compose

1. No Coolify, crie um novo recurso do tipo "Docker Compose"
2. Configure o repositório: `https://github.com/guihp/extrator-prova-pdf.git`
3. Configure as variáveis de ambiente
4. Configure os volumes persistentes
5. Deploy!

O Coolify detectará automaticamente o `docker-compose.yml` e iniciará os 3 serviços.

## 📚 Documentação

- **Guia Rápido**: [DEPLOY.md](./DEPLOY.md)
- **Guia Completo**: [COOLIFY.md](./COOLIFY.md)
- **Documentação Geral**: [README.md](./README.md)

## 🐛 Suporte

Se encontrar problemas:

1. Verifique os logs no Coolify
2. Verifique as variáveis de ambiente
3. Verifique a conectividade com PostgreSQL e Redis
4. Consulte a seção de Troubleshooting em [COOLIFY.md](./COOLIFY.md)

---

**Tudo pronto! Agora é só fazer o deploy! 🚀**

