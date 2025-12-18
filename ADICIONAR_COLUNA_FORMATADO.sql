-- Script para adicionar as colunas 'texto_formatado' e 'formatado' na tabela questoes
-- Execute este script no seu PostgreSQL
-- NOTA: Se as colunas já existem, este script não fará nada (usa IF NOT EXISTS)

-- Adicionar coluna texto_formatado se não existir
ALTER TABLE questoes 
ADD COLUMN IF NOT EXISTS texto_formatado TEXT NOT NULL DEFAULT '';

-- Adicionar coluna formatado se não existir (boolean)
ALTER TABLE questoes 
ADD COLUMN IF NOT EXISTS formatado BOOLEAN NOT NULL DEFAULT false;

-- Criar índice para melhorar performance em consultas por formato
CREATE INDEX IF NOT EXISTS idx_questoes_formatado ON questoes(formatado);

-- Verificar se as colunas foram adicionadas
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'questoes' 
AND column_name IN ('formatado', 'texto_formatado')
ORDER BY column_name;

