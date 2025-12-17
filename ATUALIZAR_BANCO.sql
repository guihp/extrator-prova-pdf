-- Script para adicionar os novos campos na tabela imagens
-- Execute este script no seu PostgreSQL

-- Adicionar campos de hash se não existirem
ALTER TABLE imagens ADD COLUMN IF NOT EXISTS hash_imagem VARCHAR(64);
ALTER TABLE imagens ADD COLUMN IF NOT EXISTS perceptual_hash VARCHAR(32);

-- Criar índice se não existir
CREATE INDEX IF NOT EXISTS idx_imagens_hash ON imagens(hash_imagem);

-- Verificar se os campos foram adicionados
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'imagens' 
AND column_name IN ('hash_imagem', 'perceptual_hash');




