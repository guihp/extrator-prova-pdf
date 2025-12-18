# Variáveis de Ambiente para Coolify

## Problemas Identificados e Correções

### ❌ Problema 1: VITE_API_BASE_URL incorreto

**Valor atual (ERRADO):**
```
VITE_API_BASE_URL=http://localhost:8000
```

**Valor correto:**
```
VITE_API_BASE_URL=https://api.flowera.com.br
```

**Por quê?** O frontend precisa saber qual é a URL da API em produção. Se estiver como `localhost:8000`, ele tentará chamar o backend local, que não existe em produção.

### ✅ Variáveis Corretas para Configurar no Coolify

#### Para Backend e Celery:

```env
# PostgreSQL (use URL completa - mais fácil)
POSTGRES_URL=postgresql://usuario:senha@host:porta/database

# APIs
GEMINI_API_KEY=sua_chave_gemini_aqui
OPENAI_API_KEY=sua_chave_openai_aqui

# Redis
REDIS_URL=redis://usuario:senha@host:porta/0

# Configurações
BASE_URL=https://api.flowera.com.br
UPLOAD_DIR=uploads
IMAGES_DIR=images
MAX_FILE_SIZE=10485760
```

**Nota:** As variáveis individuais do PostgreSQL (POSTGRES_HOST, POSTGRES_USER, etc.) podem ficar vazias se você usar POSTGRES_URL. O código prioriza POSTGRES_URL.

#### Para Frontend:

```env
# IMPORTANTE: URL da API para o frontend chamar
VITE_API_BASE_URL=https://api.flowera.com.br
```

**⚠️ CRÍTICO:** O `VITE_API_BASE_URL` deve ser definido ANTES do build do frontend, pois o Vite incorpora essa variável no código JavaScript no momento do build. Se mudar depois do build, não terá efeito.

### 🔍 Como Verificar se Está Funcionando

1. **Backend:** Acesse `https://api.flowera.com.br/health` - deve retornar `{"status":"ok"}`
2. **Frontend:** Abra o console do navegador e veja se as chamadas API estão indo para `https://api.flowera.com.br`
3. **Banco de Dados:** Verifique os logs do backend para ver se consegue conectar ao PostgreSQL

### 📝 Variáveis do Coolify (gerenciadas automaticamente)

Estas variáveis são criadas automaticamente pelo Coolify e não precisam ser definidas manualmente:

```
SERVICE_FQDN_BACKEND=api.flowera.com.br
SERVICE_FQDN_FRONTEND=app.flowera.com.br
SERVICE_URL_BACKEND=https://api.flowera.com.br
SERVICE_URL_FRONTEND=https://app.flowera.com.br
```

Você pode usá-las como referência, mas não são necessárias no código.

### 🔧 Solução para o Problema Atual

1. **No Coolify, vá em Environment Variables**
2. **Altere `VITE_API_BASE_URL` de `http://localhost:8000` para `https://api.flowera.com.br`**
3. **Certifique-se de que `BASE_URL` está como `https://api.flowera.com.br`**
4. **Faça um rebuild do frontend** (o Vite precisa rebuildar com a variável correta)

### 🐛 Debug do Problema de Banco de Dados

Se ainda não está pegando do banco:

1. Verifique os logs do container backend:
   ```bash
   # No Coolify, veja os logs do serviço backend
   ```

2. Procure por erros de conexão PostgreSQL nos logs

3. Teste a conexão manualmente:
   - A URL está correta?
   - O servidor PostgreSQL aceita conexões do IP do Coolify?
   - As credenciais estão corretas?

4. Verifique se a tabela existe:
   - Execute `postgres_schema.sql` e `ADICIONAR_COLUNA_FORMATADO.sql` no banco

