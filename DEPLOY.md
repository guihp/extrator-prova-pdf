# 🚀 Guia Rápido de Deploy

## 📦 Preparação do Repositório

O projeto está pronto para deploy! Todos os arquivos necessários foram criados:

### Arquivos Criados:
- ✅ `backend/Dockerfile` - Imagem Docker do backend
- ✅ `frontend/Dockerfile` - Imagem Docker do frontend  
- ✅ `docker-compose.yml` - Orquestração completa
- ✅ `.dockerignore` - Arquivos ignorados no build
- ✅ `COOLIFY.md` - Guia detalhado para Coolify

## 🎯 Deploy no Coolify - Passo a Passo

### Opção 1: Docker Compose (Mais Simples)

1. **No Coolify, crie um novo recurso:**
   - Tipo: `Docker Compose`
   - Repositório: `https://github.com/guihp/extrator-prova-pdf.git`
   - Branch: `main`

2. **Configure as variáveis de ambiente:**
   ```
   POSTGRES_URL=postgresql://user:password@host:port/database
   GEMINI_API_KEY=sua_chave_aqui
   OPENAI_API_KEY=sua_chave_aqui
   REDIS_URL=redis://user:password@host:port/0
   BASE_URL=https://api.seudominio.com
   VITE_API_URL=https://api.seudominio.com
   ```

3. **Configure volumes persistentes:**
   - `./backend/uploads` → `/app/uploads`
   - `./backend/images` → `/app/images`

4. **Deploy!** O Coolify detectará automaticamente o `docker-compose.yml`

### Opção 2: Serviços Individuais

#### Backend (FastAPI)

1. Tipo: `Dockerfile`
2. Dockerfile Path: `backend/Dockerfile`
3. Porta: `8000`
4. Variáveis de ambiente: (ver acima)
5. Volumes: `/app/uploads` e `/app/images`

#### Celery Worker

1. Tipo: `Dockerfile`
2. Dockerfile Path: `backend/Dockerfile`
3. Comando: `celery -A app.tasks worker --loglevel=info --pool=solo`
4. Variáveis de ambiente: (mesmas do backend)
5. Volumes: (mesmos do backend)

#### Frontend (React)

1. Tipo: `Dockerfile`
2. Dockerfile Path: `frontend/Dockerfile`
3. Porta: `80`
4. Build Args: `VITE_API_URL=https://api.seudominio.com`
5. Variáveis de ambiente: `VITE_API_URL=https://api.seudominio.com`

## ✅ Checklist Antes do Deploy

- [ ] Repositório Git configurado e código commitado
- [ ] Banco PostgreSQL acessível e schema executado (`postgres_schema.sql`)
- [ ] Redis acessível
- [ ] API Keys obtidas (Gemini e OpenAI)
- [ ] Domínios configurados (se necessário)
- [ ] Variáveis de ambiente preparadas

## 🔧 Configuração do Banco de Dados

Execute o schema SQL antes do primeiro deploy:

```bash
# Conecte ao seu PostgreSQL e execute:
psql -h seu_host -U seu_usuario -d seu_banco -f postgres_schema.sql
```

Ou deixe o sistema criar automaticamente na primeira execução.

## 🌐 Configuração de Domínios

### Se usar domínios separados:
- Backend: `api.seudominio.com` → Configure `BASE_URL` e `VITE_API_URL`
- Frontend: `seudominio.com` → Configure `VITE_API_URL` apontando para o backend

### Se usar mesmo domínio com paths:
- Configure reverse proxy no Coolify para rotear `/api` para o backend

## 📝 Comandos Úteis

### Ver logs:
```bash
# No Coolify, use a interface ou:
docker logs analize-pdf-backend
docker logs analize-pdf-celery
docker logs analize-pdf-frontend
```

### Testar API:
```bash
curl https://api.seudominio.com/health
# Deve retornar: {"status":"ok"}
```

### Testar Frontend:
```bash
curl https://seudominio.com
# Deve retornar HTML
```

## 🐛 Problemas Comuns

### Celery não processa tarefas
- Verifique se o Redis está acessível
- Verifique a variável `REDIS_URL`
- Verifique os logs do worker

### Frontend não conecta ao backend
- Verifique se `VITE_API_URL` está correto
- Verifique CORS (já configurado para `*`)
- Verifique se o backend está acessível

### Imagens não aparecem
- Verifique volumes persistentes
- Verifique permissões dos diretórios
- Verifique `BASE_URL` no backend

## 📚 Mais Informações

Para detalhes completos, veja:
- [COOLIFY.md](./COOLIFY.md) - Guia completo e detalhado
- [README.md](./README.md) - Documentação geral do projeto

---

**Pronto para deploy! 🎉**

