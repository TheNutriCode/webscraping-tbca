CREATE TABLE IF NOT EXISTS alimentos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    classe VARCHAR(255) NOT NULL,
    principal VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS variacoes_alimentos (
    id SERIAL PRIMARY KEY,
    alimento_id INTEGER REFERENCES alimentos(id),
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nutrientes_alimentos (
    id SERIAL PRIMARY KEY,
    variacao_id INTEGER REFERENCES variacoes_alimentos(id),
    componente VARCHAR(255) NOT NULL,
    unidade_medida VARCHAR(50),
    valor_por_100g VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_alimentos_codigo ON alimentos(codigo);
CREATE INDEX IF NOT EXISTS idx_variacoes_alimento_id ON variacoes_alimentos(alimento_id);
CREATE INDEX IF NOT EXISTS idx_nutrientes_variacao_id ON nutrientes_alimentos(variacao_id);
