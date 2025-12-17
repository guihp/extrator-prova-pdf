-- Corrigir tamanho do campo perceptual_hash
-- O hash pode ter até 64 caracteres, mas definimos como 64 para segurança

ALTER TABLE imagens ALTER COLUMN perceptual_hash TYPE VARCHAR(64);

-- Verificar
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'imagens' 
AND column_name = 'perceptual_hash';




