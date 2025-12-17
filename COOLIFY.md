# 🚀 Deploy no Coolify - Guia Completo

Este guia explica como fazer o deploy do Sistema de Análise de PDFs no Coolify.

## 📋 Pré-requisitos

1. Conta no Coolify configurada
2. Repositório Git configurado (GitHub: https://github.com/guihp/extrator-prova-pdf.git)
3. Banco de dados PostgreSQL acessível
4. Redis acessível
5. API Keys: Google Gemini e OpenAI

## 🏗️ Estrutura do Projeto

O projeto consiste em 3 serviços principais:

1. **Backend (FastAPI)** - API REST na porta 8000
2. **Celery Worker** - Processamento assíncrono de PDFs
3. **Frontend (React/Vite)** - Interface web na porta 80

## 📦 Configuração no Coolify

### Opção 1: Deploy com Docker Compose (Recomendado)

1. **Criar novo recurso no Coolify:**
   - Tipo: `Docker Compose`
   - Repositório: `https://github.com/guihp/extrator-prova-pdf.git`
   - Branch: `main` (ou sua branch principal)

2. **Configurar variáveis de ambiente:**
   ```
   POSTGRES_URL=postgresql://user:password@host:port/database
   GEMINI_API_KEY=sua_chave_gemini
   OPENAI_API_KEY=sua_chave_openai
   REDIS_URL=redis://user:password@host:port/0
   BASE_URL=https://seu-dominio.com
   VITE_API_URL=https://seu-dominio.com
   ```

3. **Configurar volumes persistentes:**
   - `./backend/uploads` → `/app/uploads`
   - `./backend/images` → `/app/images`

4. **Deploy:**
   - Coolify detectará automaticamente o `docker-compose.yml`
   - Os 3 serviços serão iniciados automaticamente

### Opção 2: Deploy Individual de Serviços

#### Backend (FastAPI)

1. **Criar novo recurso:**
   - Tipo: `Dockerfile`
   - Repositório: `https://github.com/guihp/extrator-prova-pdf.git`
   - Dockerfile Path: `backend/Dockerfile`
   - Porta: `8000`

2. **Variáveis de ambiente:**
   ```
   POSTGRES_URL=postgresql://user:password@host:port/database
   GEMINI_API_KEY=sua_chave_gemini
   OPENAI_API_KEY=sua_chave_openai
   REDIS_URL=redis://user:password@host:port/0
   BASE_URL=https://seu-dominio-backend.com
   ```

3. **Volumes:**
   - `/app/uploads` (persistente)
   - `/app/images` (persistente)

#### Celery Worker

1. **Criar novo recurso:**
   - Tipo: `Dockerfile`
   - Repositório: `https://github.com/guihp/extrator-prova-pdf.git`
   - Dockerfile Path: `backend/Dockerfile`
   - Comando customizado: `celery -A app.tasks worker --loglevel=info --pool=solo`

2. **Variáveis de ambiente:** (mesmas do backend)

3. **Volumes:** (mesmos do backend)

#### Frontend (React)

1. **Criar novo recurso:**
   - Tipo: `Dockerfile`
   - Repositório: `https://github.com/guihp/extrator-prova-pdf.git`
   - Dockerfile Path: `frontend/Dockerfile`
   - Porta: `80`

2. **Build Arguments:**
   ```
   VITE_API_URL=https://seu-dominio-backend.com
   ```

3. **Variáveis de ambiente:**
   ```
   VITE_API_URL=https://seu-dominio-backend.com
   ```

## 🔧 Configurações Importantes

### 1. Banco de Dados PostgreSQL

Execute o schema SQL antes do primeiro deploy:

```sql
-- Arquivo: postgres_schema.sql
-- Execute no seu banco PostgreSQL
```

Ou deixe o sistema criar automaticamente na primeira execução.

### 2. Redis

Configure o Redis antes do deploy. O Celery precisa do Redis para funcionar.

### 3. Tesseract OCR

O Dockerfile do backend já inclui o Tesseract OCR com suporte a português e inglês.

### 4. Volumes Persistentes

**IMPORTANTE:** Configure volumes persistentes para:
- `uploads/` - PDFs enviados
- `images/` - Imagens extraídas

Sem volumes persistentes, os dados serão perdidos ao reiniciar os containers.

## 🌐 Configuração de Domínio

### Backend

Configure o domínio do backend (ex: `api.seudominio.com`) e defina:
```
BASE_URL=https://api.seudominio.com
```

### Frontend

Configure o domínio do frontend (ex: `seudominio.com`) e defina:
```
VITE_API_URL=https://api.seudominio.com
```

O frontend fará requisições para o backend usando esta URL.

## 🔄 Fluxo de Deploy

1. **Push para o repositório Git**
2. **Coolify detecta mudanças** (se webhook configurado)
3. **Build das imagens Docker**
4. **Deploy dos containers**
5. **Health checks** verificam se os serviços estão funcionando

## 🧪 Verificação Pós-Deploy

1. **Backend Health Check:**
   ```bash
   curl https://api.seudominio.com/health
   # Deve retornar: {"status":"ok"}
   ```

2. **Frontend:**
   ```bash
   curl https://seudominio.com
   # Deve retornar HTML da aplicação
   ```

3. **API Endpoints:**
   ```bash
   curl https://api.seudominio.com/api/provas
   # Deve retornar lista de provas (pode estar vazia)
   ```

## 🐛 Troubleshooting

### Erro: "Connection refused" no Celery

- Verifique se o Redis está acessível
- Verifique a variável `REDIS_URL`
- Verifique se o worker Celery está rodando

### Erro: "PostgreSQL connection failed"

- Verifique se o banco está acessível
- Verifique a variável `POSTGRES_URL`
- Verifique se o schema foi executado

### Frontend não conecta ao backend

- Verifique se `VITE_API_URL` está correto
- Verifique CORS no backend (já configurado para `*`)
- Verifique se o backend está acessível

### Imagens não aparecem

- Verifique se os volumes estão montados corretamente
- Verifique se o diretório `images/` existe e tem permissões
- Verifique a variável `BASE_URL` no backend

## 📝 Notas Importantes

1. **Pool do Celery:** No macOS, usamos `--pool=solo`. No Linux, pode usar `prefork` para melhor performance.

2. **Tesseract OCR:** Já incluído no Dockerfile do backend. Não precisa instalação adicional.

3. **Processamento Assíncrono:** O Celery Worker processa PDFs em background. Certifique-se de que está rodando.

4. **Limites de Upload:** O tamanho máximo de arquivo é 10MB por padrão. Pode ser ajustado na variável `MAX_FILE_SIZE`.

## 🔐 Segurança

- **NUNCA** commite arquivos `.env` no Git
- Use variáveis de ambiente do Coolify para secrets
- Configure CORS adequadamente em produção
- Use HTTPS para todas as conexões

## 📚 Recursos Adicionais

- [Documentação do Coolify](https://coolify.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

## ✅ Checklist de Deploy

- [ ] Repositório Git configurado
- [ ] Banco PostgreSQL acessível e schema executado
- [ ] Redis acessível
- [ ] API Keys configuradas (Gemini e OpenAI)
- [ ] Variáveis de ambiente configuradas no Coolify
- [ ] Volumes persistentes configurados
- [ ] Domínios configurados
- [ ] Health checks passando
- [ ] Teste de upload de PDF funcionando

---

**Pronto para deploy! 🚀**

