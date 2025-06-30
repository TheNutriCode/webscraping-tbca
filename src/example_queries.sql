-- Example queries for the new column-based nutrient database

-- 1. Get basic food information with all its nutrients
SELECT 
    f.code, 
    f.name, 
    f.group,
    fv.description,
    fvn.*
FROM 
    foods f
JOIN 
    food_variations fv ON f.id = fv.food_id
JOIN 
    food_variation_nutrients fvn ON fv.id = fvn.variation_id
WHERE 
    f.code = 'BRC0001C'  -- Replace with any food code you want to query
LIMIT 1;

-- 2. Get foods with the highest protein content
SELECT 
    f.name, 
    f.group,
    fvn.proteina_g
FROM 
    foods f
JOIN 
    food_variations fv ON f.id = fv.food_id
JOIN 
    food_variation_nutrients fvn ON fv.id = fvn.variation_id
WHERE 
    fvn.proteina_g IS NOT NULL
ORDER BY 
    fvn.proteina_g DESC
LIMIT 10;

-- 3. Get foods with high vitamin C and low fat
SELECT 
    f.name, 
    f.group,
    fvn.vitamina_c_mg,
    fvn.lipidios_g
FROM 
    foods f
JOIN 
    food_variations fv ON f.id = fv.food_id
JOIN 
    food_variation_nutrients fvn ON fv.id = fvn.variation_id
WHERE 
    fvn.vitamina_c_mg > 50  -- High vitamin C (>50mg)
    AND fvn.lipidios_g < 3  -- Low fat (<3g)
    AND fvn.vitamina_c_mg IS NOT NULL
    AND fvn.lipidios_g IS NOT NULL
ORDER BY 
    fvn.vitamina_c_mg DESC;

-- 4. Calculate energy distribution (percentage of calories from each macronutrient)
SELECT 
    f.name,
    f.group,
    fvn.energia_kcal,
    fvn.proteina_g,
    fvn.carboidrato_total_g,
    fvn.lipidios_g,
    ROUND((fvn.proteina_g * 4 * 100) / NULLIF(fvn.energia_kcal, 0), 1) AS protein_percent,
    ROUND((fvn.carboidrato_total_g * 4 * 100) / NULLIF(fvn.energia_kcal, 0), 1) AS carb_percent,
    ROUND((fvn.lipidios_g * 9 * 100) / NULLIF(fvn.energia_kcal, 0), 1) AS fat_percent
FROM 
    foods f
JOIN 
    food_variations fv ON f.id = fv.food_id
JOIN 
    food_variation_nutrients fvn ON fv.id = fvn.variation_id
WHERE 
    fvn.energia_kcal IS NOT NULL 
    AND fvn.proteina_g IS NOT NULL
    AND fvn.carboidrato_total_g IS NOT NULL
    AND fvn.lipidios_g IS NOT NULL
    AND fvn.energia_kcal > 0
LIMIT 20;

-- 5. Find foods rich in specific minerals (calcium and iron)
SELECT 
    f.name, 
    f.group,
    fvn.calcio_mg,
    fvn.ferro_mg
FROM 
    foods f
JOIN 
    food_variations fv ON f.id = fv.food_id
JOIN 
    food_variation_nutrients fvn ON fv.id = fvn.variation_id
WHERE 
    fvn.calcio_mg > 100  -- Good calcium source (>100mg)
    AND fvn.ferro_mg > 1.8  -- Good iron source (>1.8mg)
    AND fvn.calcio_mg IS NOT NULL
    AND fvn.ferro_mg IS NOT NULL
ORDER BY 
    (fvn.calcio_mg + fvn.ferro_mg * 50) DESC;  -- Weighted sorting for both nutrients

-- 6. Foods low in sodium (for low-sodium diets)
SELECT 
    f.name, 
    f.group,
    fvn.sodio_mg
FROM 
    foods f
JOIN 
    food_variations fv ON f.id = fv.food_id
JOIN 
    food_variation_nutrients fvn ON fv.id = fvn.variation_id
WHERE 
    fvn.sodio_mg < 140  -- Low sodium (<140mg per 100g)
    AND fvn.sodio_mg IS NOT NULL
    AND fvn.sodio_mg >= 0
ORDER BY 
    fvn.sodio_mg ASC;

-- 7. Comparison of similar foods (e.g., different types of fruits)
SELECT 
    f.name,
    fvn.carboidrato_total_g AS carbs,
    fvn.fibra_alimentar_g AS fiber,
    fvn.vitamina_c_mg AS vit_c
FROM 
    foods f
JOIN 
    food_variations fv ON f.id = fv.food_id
JOIN 
    food_variation_nutrients fvn ON fv.id = fvn.variation_id
WHERE 
    f.group = 'Frutas e derivados'
    AND fvn.carboidrato_total_g IS NOT NULL
    AND fvn.fibra_alimentar_g IS NOT NULL
ORDER BY 
    f.name ASC;

-- 8. Calculate nutrient density score (nutrients per calorie)
SELECT 
    f.name,
    f.group,
    fvn.energia_kcal,
    (
        COALESCE(fvn.proteina_g, 0) + 
        COALESCE(fvn.fibra_alimentar_g, 0) * 2 + 
        COALESCE(fvn.vitamina_c_mg/60, 0) + 
        COALESCE(fvn.ferro_mg/8, 0) + 
        COALESCE(fvn.calcio_mg/800, 0) + 
        COALESCE(fvn.vitamina_a_re_mcg/800, 0)
    ) / NULLIF(fvn.energia_kcal/100, 0) AS nutrient_density_score
FROM 
    foods f
JOIN 
    food_variations fv ON f.id = fv.food_id
JOIN 
    food_variation_nutrients fvn ON fv.id = fvn.variation_id
WHERE 
    fvn.energia_kcal > 0
    AND fvn.energia_kcal IS NOT NULL
ORDER BY 
    nutrient_density_score DESC
LIMIT 20;
