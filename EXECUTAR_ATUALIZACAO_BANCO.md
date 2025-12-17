# 🔧 Atualizar Banco de Dados

## ⚠️ ERRO: `column imagens.hash_imagem does not exist`

Este erro ocorre porque o banco de dados não tem os novos campos que foram adicionados.

## ✅ Solução

Execute o script SQL `ATUALIZAR_BANCO.sql` no seu PostgreSQL.

### Opção 1: Via psql (linha de comando)

```bash
# Conectar ao PostgreSQL
psql "postgres://postgres:DvMaicTTXDkVL6r5YReP9sQX0ihs8W7DGbkWJhbsoh0BDdKhdsTQCWQUz2o2CA7F@72.60.146.143:5435/postgres"

# Executar o script
\i ATUALIZAR_BANCO.sql

# Ou copiar e colar o conteúdo do arquivo
```

### Opção 2: Via Python (automático)

```bash
cd backend
source venv/bin/activate
python3 -c "
from app.services.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('ALTER TABLE imagens ADD COLUMN IF NOT EXISTS hash_imagem VARCHAR(64)'))
    conn.execute(text('ALTER TABLE imagens ADD COLUMN IF NOT EXISTS perceptual_hash VARCHAR(32)'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_imagens_hash ON imagens(hash_imagem)'))
    conn.commit()
    print('✅ Campos adicionados com sucesso!')
"
```

### Opção 3: Via cliente gráfico (pgAdmin, DBeaver, etc.)

1. Abra seu cliente PostgreSQL
2. Conecte ao banco
3. Execute o conteúdo do arquivo `ATUALIZAR_BANCO.sql`

## 📋 Conteúdo do Script

```sql
-- Adicionar campos de hash se não existirem
ALTER TABLE imagens ADD COLUMN IF NOT EXISTS hash_imagem VARCHAR(64);
ALTER TABLE imagens ADD COLUMN IF NOT EXISTS perceptual_hash VARCHAR(32);

-- Criar índice se não existir
CREATE INDEX IF NOT EXISTS idx_imagens_hash ON imagens(hash_imagem);
```

## ✅ Verificar se funcionou

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'imagens' 
AND column_name IN ('hash_imagem', 'perceptual_hash');
```

Deve retornar 2 linhas com os campos `hash_imagem` e `perceptual_hash`.

## 🔄 Após atualizar

Reinicie o FastAPI para aplicar as mudanças:

```bash
# Parar FastAPI
pkill -f "uvicorn.*app.main"

# Reiniciar
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```




