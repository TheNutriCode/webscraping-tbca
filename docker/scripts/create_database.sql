CREATE TABLE IF NOT EXISTS foods (
    id SERIAL PRIMARY KEY,
    code VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    group VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nutrient (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES nutrient_category(id),
    name VARCHAR(500) NOT NULL UNIQUE,
    unit VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nutrient_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS food_nutrients (
    id SERIAL PRIMARY KEY,
    food_id INTEGER REFERENCES food(id),
    
    -- Energy and macronutrients
    energia_kj DECIMAL(10,2),
    energia_kcal DECIMAL(10,2),
    umidade_g DECIMAL(10,2),
    carboidrato_total_g DECIMAL(10,2),
    carboidrato_disponivel_g DECIMAL(10,2),
    proteina_g DECIMAL(10,2),
    lipidios_g DECIMAL(10,2),
    fibra_alimentar_g DECIMAL(10,2),
    alcool_g DECIMAL(10,2),
    cinzas_g DECIMAL(10,2),
    
    -- Lipid-related nutrients
    colesterol_mg DECIMAL(10,2),
    acidos_graxos_saturados_g DECIMAL(10,2),
    acidos_graxos_monoinsaturados_g DECIMAL(10,2),
    acidos_graxos_poliinsaturados_g DECIMAL(10,2),
    acidos_graxos_trans_g DECIMAL(10,2),
    
    -- Minerals
    calcio_mg DECIMAL(10,2),
    ferro_mg DECIMAL(10,2),
    sodio_mg DECIMAL(10,2),
    magnesio_mg DECIMAL(10,2),
    fosforo_mg DECIMAL(10,2),
    potassio_mg DECIMAL(10,2),
    manganes_mg DECIMAL(10,2),
    zinco_mg DECIMAL(10,2),
    cobre_mg DECIMAL(10,2),
    selenio_mcg DECIMAL(10,2),
    
    -- Vitamins
    vitamina_a_re_mcg DECIMAL(10,2),
    vitamina_a_rae_mcg DECIMAL(10,2),
    vitamina_d_mcg DECIMAL(10,2),
    alfa_tocoferol_mg DECIMAL(10,2),
    tiamina_mg DECIMAL(10,2),
    riboflavina_mg DECIMAL(10,2),
    niacina_mg DECIMAL(10,2),
    vitamina_b6_mg DECIMAL(10,2),
    vitamina_b12_mcg DECIMAL(10,2),
    vitamina_c_mg DECIMAL(10,2),
    equivalente_folato_mcg DECIMAL(10,2),
    
    -- Additional nutrients
    sal_de_adicao_g DECIMAL(10,2),
    acucar_de_adicao_g DECIMAL(10,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_foods_code ON foods(code);
CREATE INDEX IF NOT EXISTS idx_food_nutrients_food_id ON food_nutrients(food_id);