import json
import psycopg2
from dbconnect import postgresql_connection

def populate_nutrients_table():
    """Populates the nutrients reference table with unique nutrients from the list"""
    
    # List of nutrients with their units based on the provided data
    nutrients = [
        {"name": "Energia", "unit": "kJ", "category": "Energy"},
        {"name": "Energia", "unit": "kcal", "category": "Energy"},
        {"name": "Umidade", "unit": "g", "category": "Basic"},
        {"name": "Carboidrato total", "unit": "g", "category": "Macronutrient"},
        {"name": "Carboidrato disponível", "unit": "g", "category": "Macronutrient"},
        {"name": "Proteína", "unit": "g", "category": "Macronutrient"},
        {"name": "Lipídios", "unit": "g", "category": "Macronutrient"},
        {"name": "Fibra alimentar", "unit": "g", "category": "Macronutrient"},
        {"name": "Álcool", "unit": "g", "category": "Other"},
        {"name": "Cinzas", "unit": "g", "category": "Other"},
        {"name": "Colesterol", "unit": "mg", "category": "Lipid"},
        {"name": "Ácidos graxos saturados", "unit": "g", "category": "Lipid"},
        {"name": "Ácidos graxos monoinsaturados", "unit": "g", "category": "Lipid"},
        {"name": "Ácidos graxos poliinsaturados", "unit": "g", "category": "Lipid"},
        {"name": "Ácidos graxos trans", "unit": "g", "category": "Lipid"},
        {"name": "Cálcio", "unit": "mg", "category": "Mineral"},
        {"name": "Ferro", "unit": "mg", "category": "Mineral"},
        {"name": "Sódio", "unit": "mg", "category": "Mineral"},
        {"name": "Magnésio", "unit": "mg", "category": "Mineral"},
        {"name": "Fósforo", "unit": "mg", "category": "Mineral"},
        {"name": "Potássio", "unit": "mg", "category": "Mineral"},
        {"name": "Manganês", "unit": "mg", "category": "Mineral"},
        {"name": "Zinco", "unit": "mg", "category": "Mineral"},
        {"name": "Cobre", "unit": "mg", "category": "Mineral"},
        {"name": "Selênio", "unit": "mcg", "category": "Mineral"},
        {"name": "Vitamina A (RE)", "unit": "mcg", "category": "Vitamin"},
        {"name": "Vitamina A (RAE)", "unit": "mcg", "category": "Vitamin"},
        {"name": "Vitamina D", "unit": "mcg", "category": "Vitamin"},
        {"name": "Alfa-tocoferol (Vitamina E)", "unit": "mg", "category": "Vitamin"},
        {"name": "Tiamina", "unit": "mg", "category": "Vitamin"},
        {"name": "Riboflavina", "unit": "mg", "category": "Vitamin"},
        {"name": "Niacina", "unit": "mg", "category": "Vitamin"},
        {"name": "Vitamina B6", "unit": "mg", "category": "Vitamin"},
        {"name": "Vitamina B12", "unit": "mcg", "category": "Vitamin"},
        {"name": "Vitamina C", "unit": "mg", "category": "Vitamin"},
        {"name": "Equivalente de folato", "unit": "mcg", "category": "Vitamin"},
        {"name": "Sal de adição", "unit": "g", "category": "Other"},
        {"name": "Açúcar de adição", "unit": "g", "category": "Other"}
    ]
    
    conn = postgresql_connection()
    cursor = conn.cursor()
    
    try:
        # Insert nutrients
        for nutrient in nutrients:
            # Check if the nutrient already exists
            cursor.execute(
                "SELECT id FROM nutrients WHERE name = %s AND unit_of_measurement = %s",
                (nutrient["name"], nutrient["unit"])
            )
            
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO nutrients (name, unit_of_measurement, category) VALUES (%s, %s, %s)",
                    (nutrient["name"], nutrient["unit"], nutrient["category"])
                )
        
        conn.commit()
        print(f"Successfully populated nutrients table with {len(nutrients)} nutrients")
    except Exception as e:
        conn.rollback()
        print(f"Error populating nutrients table: {e}")
    finally:
        cursor.close()
        conn.close()

def migrate_data():
    """Migrates data from old food_nutrients to new food_variation_nutrients table"""
    
    conn = postgresql_connection()
    cursor = conn.cursor()
    
    try:
        # Get all food variations
        cursor.execute("SELECT id FROM food_variations")
        variation_ids = [row[0] for row in cursor.fetchall()]
        
        # Create a mapping of nutrient names to column names
        nutrient_column_map = {
            "Energia (kJ)": "energia_kj",
            "Energia (kcal)": "energia_kcal",
            "Energia": "energia_kj",  # Handle cases where unit is separate
            "Umidade": "umidade_g",
            "Carboidrato total": "carboidrato_total_g",
            "Carboidrato disponível": "carboidrato_disponivel_g",
            "Proteína": "proteina_g",
            "Lipídios": "lipidios_g",
            "Fibra alimentar": "fibra_alimentar_g",
            "Álcool": "alcool_g",
            "Cinzas": "cinzas_g",
            "Colesterol": "colesterol_mg",
            "Ácidos graxos saturados": "acidos_graxos_saturados_g",
            "Ácidos graxos monoinsaturados": "acidos_graxos_monoinsaturados_g",
            "Ácidos graxos poliinsaturados": "acidos_graxos_poliinsaturados_g",
            "Ácidos graxos trans": "acidos_graxos_trans_g",
            "Cálcio": "calcio_mg",
            "Ferro": "ferro_mg",
            "Sódio": "sodio_mg",
            "Magnésio": "magnesio_mg",
            "Fósforo": "fosforo_mg",
            "Potássio": "potassio_mg",
            "Manganês": "manganes_mg",
            "Zinco": "zinco_mg",
            "Cobre": "cobre_mg",
            "Selênio": "selenio_mcg",
            "Vitamina A (RE)": "vitamina_a_re_mcg",
            "Vitamina A (RAE)": "vitamina_a_rae_mcg",
            "Vitamina D": "vitamina_d_mcg",
            "Alfa-tocoferol (Vitamina E)": "alfa_tocoferol_mg",
            "Tiamina": "tiamina_mg",
            "Riboflavina": "riboflavina_mg",
            "Niacina": "niacina_mg",
            "Vitamina B6": "vitamina_b6_mg",
            "Vitamina B12": "vitamina_b12_mcg",
            "Vitamina C": "vitamina_c_mg",
            "Equivalente de folato": "equivalente_folato_mcg",
            "Sal de adição": "sal_de_adicao_g",
            "Açúcar de adição": "acucar_de_adicao_g"
        }
        
        count = 0
        for variation_id in variation_ids:
            # Get all nutrients for this variation
            cursor.execute(
                "SELECT component, unit_of_measurement, value_per_100g FROM food_nutrients WHERE variation_id = %s",
                (variation_id,)
            )
            nutrients_data = cursor.fetchall()
            
            # Skip if no nutrients
            if not nutrients_data:
                continue
            
            # Create a dictionary to store nutrient values
            nutrient_values = {}
            
            # Process each nutrient
            for component, unit, value in nutrients_data:
                # Create a key for the nutrient (either with unit or without)
                nutrient_key = f"{component} ({unit})" if unit else component
                
                # Find the corresponding column name
                column_name = nutrient_column_map.get(nutrient_key) or nutrient_column_map.get(component)
                
                if column_name:
                    # Convert value to numeric if possible
                    try:
                        numeric_value = float(value.replace(',', '.')) if value and value.strip() != "NA" else None
                    except (ValueError, AttributeError):
                        numeric_value = None
                    
                    nutrient_values[column_name] = numeric_value
            
            # Only proceed if we have values to insert
            if nutrient_values:
                # Check if entry already exists
                cursor.execute(
                    "SELECT id FROM food_variation_nutrients WHERE variation_id = %s",
                    (variation_id,)
                )
                
                if cursor.fetchone() is None:
                    # Build the INSERT query
                    columns = ['variation_id'] + list(nutrient_values.keys())
                    placeholders = ['%s'] * len(columns)
                    values = [variation_id] + list(nutrient_values.values())
                    
                    query = f"""
                        INSERT INTO food_variation_nutrients 
                        ({', '.join(columns)}) 
                        VALUES ({', '.join(placeholders)})
                    """
                    
                    cursor.execute(query, values)
                    count += 1
        
        conn.commit()
        print(f"Successfully migrated {count} food variations to the new structure")
    except Exception as e:
        conn.rollback()
        print(f"Error migrating data: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Starting database migration...")
    # First populate the nutrients reference table
    populate_nutrients_table()
    # Then migrate the data
    migrate_data()
    print("Migration completed!")
