-- Schema PostgreSQL para o sistema de análise de PDFs

-- Tabela de provas
CREATE TABLE IF NOT EXISTS provas (
    id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    arquivo_original VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'processando',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de questões
CREATE TABLE IF NOT EXISTS questoes (
    id BIGSERIAL PRIMARY KEY,
    prova_id BIGINT NOT NULL REFERENCES provas(id) ON DELETE CASCADE,
    numero INTEGER NOT NULL,
    texto TEXT NOT NULL,
    ordem INTEGER NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(prova_id, numero)
);

-- Tabela de imagens
CREATE TABLE IF NOT EXISTS imagens (
    id BIGSERIAL PRIMARY KEY,
    prova_id BIGINT NOT NULL REFERENCES provas(id) ON DELETE CASCADE,
    questao_id BIGINT REFERENCES questoes(id) ON DELETE SET NULL,
    caminho_arquivo TEXT NOT NULL,
    posicao_pagina INTEGER NOT NULL,
    hash_imagem VARCHAR(64),
    perceptual_hash VARCHAR(64),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_questoes_prova_id ON questoes(prova_id);
CREATE INDEX IF NOT EXISTS idx_questoes_numero ON questoes(prova_id, numero);
CREATE INDEX IF NOT EXISTS idx_imagens_prova_id ON imagens(prova_id);
CREATE INDEX IF NOT EXISTS idx_imagens_questao_id ON imagens(questao_id);
CREATE INDEX IF NOT EXISTS idx_imagens_hash ON imagens(hash_imagem);
CREATE INDEX IF NOT EXISTS idx_provas_status ON provas(status);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_provas_updated_at BEFORE UPDATE ON provas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();



