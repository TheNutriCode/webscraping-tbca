import json
import requests
from bs4 import BeautifulSoup
from dbconnect import postgresql_connection

class TBCAProcessor:
    def __init__(self, file_path="data/foods.txt"):
        self.file_path = file_path
        
    def process_description(self, description):
        """Processes description, extracting main part and observations"""
        parts = description.split(",")
        main_part = parts[0].strip()
        observations = [part.strip().replace("s/", "without").replace("c/", "with") for part in parts[1:]]
        observations_line = ", ".join(observations) if observations else main_part
        return main_part, observations_line
    
    def save_to_file(self, food_json):
        """Saves data to the TXT file"""
        import os
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "a", encoding='utf-8') as file:
            product_json_str = json.dumps(food_json, ensure_ascii=False)
            file.write(product_json_str + "\n")
    
    def save_to_db(self, cursor, food_json):
        """Saves data to the PostgreSQL database using the optimized column-based schema"""
        try:
            main_part, observations_line = self.process_description(food_json['description'])
            
            # Insert main food
            cursor.execute("""
                INSERT INTO foods (code, name, group) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (code) DO NOTHING
                RETURNING id
            """, (food_json['code'], food_json['class'], main_part))
            
            result = cursor.fetchone()
            if result:
                food_id = result[0]
            else:
                cursor.execute("SELECT id FROM foods WHERE code = %s", 
                                (food_json['code'],))
                food_id = cursor.fetchone()[0]
            
            # Insert variation
            cursor.execute("""
                INSERT INTO food_variations (food_id, description) 
                VALUES (%s, %s) 
                RETURNING id
            """, (food_id, observations_line))
            
            variation_id = cursor.fetchone()[0]
            
            # Create a mapping of nutrient components to database columns
            nutrient_column_map = {
                "Energia": "energia_kj" if "kJ" in str(food_json['nutrients']) else "energia_kcal",
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
            
            # Dictionary to store nutrient values for the column-based approach
            nutrient_values = {"variation_id": variation_id}
            
            # Also insert into the legacy table for backward compatibility
            for nutrient in food_json['nutrients']:
                # Ensure all values are truncated to appropriate lengths
                component = nutrient.get('Component', '')[:499]  # Truncate to fit VARCHAR(500)
                unit = nutrient.get('Units', '')[:99]           # Truncate to fit VARCHAR(100)
                value = nutrient.get('Value per 100g', '')[:99]  # Truncate to fit VARCHAR(100)
                
                # Insert into legacy table
                cursor.execute("""
                    INSERT INTO food_nutrients 
                    (variation_id, component, unit_of_measurement, value_per_100g) 
                    VALUES (%s, %s, %s, %s)
                """, (
                    variation_id,
                    component,
                    unit,
                    value
                ))
                
                # Populate the dictionary for the column-based approach
                column_name = nutrient_column_map.get(component)
                if column_name:
                    # Convert value to numeric if possible
                    try:
                        numeric_value = float(value.replace(',', '.')) if value and value not in ("NA", "") else None
                    except (ValueError, AttributeError):
                        numeric_value = None
                        
                    nutrient_values[column_name] = numeric_value
            
            # Build the dynamic SQL for the column-based table
            if nutrient_values:
                columns = list(nutrient_values.keys())
                placeholders = ['%s'] * len(columns)
                values = [nutrient_values[col] for col in columns]
                
                query = f"""
                    INSERT INTO food_variation_nutrients 
                    ({', '.join(columns)}) 
                    VALUES ({', '.join(placeholders)})
                """
                
                cursor.execute(query, values)
                
        except Exception as e:
            # Log the error but don't stop processing
            print(f"Error saving to database: {e}")
            print(f"Food data: {food_json}")
            # Rollback this transaction
            cursor.connection.rollback()
            return False
            
        return True

def run_webscraping(save_to_file=True, save_to_db=True):
    processor = TBCAProcessor()
    
    base_url = 'https://www.tbca.net.br/base-dados/composicao_alimentos.php'
    food_codes = []
    params = {'page': 1}
    
    conn = cursor = None
    if save_to_db:
        conn = postgresql_connection()
        cursor = conn.cursor()
    
    print("Collecting food codes...")
    
    while True:
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Search for food links on the page
            food_links = soup.find_all('a', href=lambda x: x and 'int_composicao_alimentos.php?cod_produto=' in x)
            
            for link in food_links:
                href = link.get('href')
                food_code = href.split('cod_produto=')[1].split('&')[0]
                # Extract food class (if available in context)
                food_class = link.find_parent('tr').find_all('td')[3].get_text().strip()
                food_codes.append((food_code, food_class))

            # Find the link to the next page
            next_page_link = soup.find('a', string='próxima »')
            
            # If there is a next page, get the URL and continue the loop
            if next_page_link:
                params['page'] += 1
            else:
                break
            
        except Exception as e:
            print(f"Error processing page {params['page']}: {e}")
            break
    
    print(f"Total foods collected: {len(food_codes)}")
    
    # Process each food
    success_count = 0
    for i, (food_code, food_class) in enumerate(food_codes):
        try:
            # Make request to individual food page
            food_url = f"{base_url}?codigo_alimento={food_code}"
            response = requests.get(food_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract food description
            description = "Description not found"
            description_elem = soup.find('h2') or soup.find('h1') or soup.find('title')
            if description_elem:
                description = description_elem.get_text().strip()
            
            # Extract nutrients table
            nutrients = []
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) >= 3:
                        nutrient = {
                            'Component': columns[0].get_text().strip(),
                            'Units': columns[1].get_text().strip(),
                            'Value per 100g': columns[2].get_text().strip()
                        }
                        nutrients.append(nutrient)
            
            food_json = {
                'code': food_code,
                'class': food_class,
                'description': description,
                'nutrients': nutrients
            }
            
            if save_to_file:
                processor.save_to_file(food_json)
            
            if save_to_db:
                success = processor.save_to_db(cursor, food_json)
                if success:
                    success_count += 1
                
                # Periodic commit
                if (i + 1) % 10 == 0:
                    conn.commit()
                    print(f"Processed {i + 1} foods, successfully saved {success_count}...")
                    
        except Exception as e:
            print(f"Error processing {food_code}: {e}")
    
    # Finalizing
    if save_to_db:
        conn.commit()
        cursor.close()
        conn.close()
    
    print(f"Web scraping finished! Successfully saved {success_count} out of {len(food_codes)} foods.")

def process_existing_file():
    """Processes existing TXT file into the database"""
    processor = TBCAProcessor()
    conn = postgresql_connection()
    cursor = conn.cursor()
    
    success_count = 0
    total_count = 0
    
    try:
        with open(processor.file_path, "r", encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    total_count += 1
                    try:
                        food_json = json.loads(line.strip())
                        success = processor.save_to_db(cursor, food_json)
                        if success:
                            success_count += 1
                            
                        # Periodic commit
                        if total_count % 10 == 0:
                            conn.commit()
                            print(f"Processed {total_count} foods, successfully saved {success_count}...")
                            
                    except Exception as e:
                        print(f"Error processing line: {e}")
                        # Continue with the next line
        
        conn.commit()
        print(f"File processing finished! Successfully saved {success_count} out of {total_count} foods.")
    except Exception as e:
        print(f"Error opening or processing the file: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # To run a full scrape
    run_webscraping(save_to_file=False, save_to_db=True)
    
    # To process only an existing file
    # process_existing_file()
