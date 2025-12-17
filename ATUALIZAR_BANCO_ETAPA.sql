-- Adicionar colunas etapa e progresso na tabela provas
ALTER TABLE provas 
ADD COLUMN IF NOT EXISTS etapa TEXT,
ADD COLUMN IF NOT EXISTS progresso INTEGER DEFAULT 0;

-- Criar índice para melhorar performance em consultas por status
CREATE INDEX IF NOT EXISTS idx_provas_status ON provas(status);
CREATE INDEX IF NOT EXISTS idx_provas_progresso ON provas(progresso);




