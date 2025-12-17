# Guia de Configuração - Sistema de Análise de PDFs

## Passo a Passo para Configurar o Sistema

### 1. Configuração do Supabase

1. Acesse [supabase.com](https://supabase.com) e crie uma conta/projeto
2. No SQL Editor, execute o script `supabase_schema.sql`
3. Vá em Storage e crie um bucket chamado `provas-images` (ou ajuste no código)
4. Configure o bucket como público
5. Anote as credenciais:
   - URL do projeto
   - Anon Key
   - Service Role Key

### 2. Configuração do Backend

1. Entre na pasta `backend`:
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
cp env.example.txt .env
# Edite o .env com suas credenciais
```

5. Preencha o arquivo `.env` com:
   - Credenciais do Supabase
   - API Key do Google Gemini (obtenha em [Google AI Studio](https://makersuite.google.com/app/apikey))
   - API Key da OpenAI (obtenha em [platform.openai.com](https://platform.openai.com/api-keys))

### 3. Configuração do Redis

**Opção 1: Docker (Recomendado)**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Opção 2: Instalação Local**
- macOS: `brew install redis` e `brew services start redis`
- Linux: `sudo apt-get install redis-server` e `sudo systemctl start redis`
- Windows: Baixe do [redis.io](https://redis.io/download)

### 4. Executar o Backend

**Terminal 1 - Worker Celery:**
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 2 - Servidor FastAPI:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Configuração do Frontend

1. Entre na pasta `frontend`:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Execute o servidor de desenvolvimento:
```bash
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

### 6. Testar o Sistema

1. Acesse `http://localhost:3000`
2. Faça upload de um PDF de prova
3. Acompanhe o processamento na interface
4. Quando concluído, expanda a prova para ver questões e imagens

## Troubleshooting

### Erro: "Redis connection refused"
- Certifique-se de que o Redis está rodando
- Verifique a URL no `.env`: `REDIS_URL=redis://localhost:6379/0`

### Erro: "Supabase connection failed"
- Verifique as credenciais no `.env`
- Confirme que o bucket `provas-images` foi criado

### Erro: "API Key inválida"
- Verifique as chaves do Gemini e OpenAI no `.env`
- Confirme que as chaves estão ativas e têm créditos

### Celery não processa tarefas
- Verifique se o worker está rodando
- Confira os logs do Celery para erros
- Verifique a conexão com Redis

## Estrutura de Dados no Supabase

Após o processamento, você terá:

- **Tabela `provas`**: Informações gerais das provas
- **Tabela `questoes`**: Questões extraídas com texto completo
- **Tabela `imagens`**: Imagens extraídas com referência às questões
- **Storage `provas-images`**: Arquivos de imagem organizados por prova

## Próximos Passos

- Configure autenticação se necessário
- Ajuste as políticas RLS no Supabase conforme sua necessidade
- Personalize os prompts de IA para melhor precisão
- Configure monitoramento e logs em produção

