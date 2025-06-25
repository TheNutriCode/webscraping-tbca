import json
import requests
from bs4 import BeautifulSoup
from dbconnect import postgresql_connection

class TBCAProcessor:
    def __init__(self, arquivo_path="../data/alimentos.txt"):
        self.arquivo_path = arquivo_path
        
    def processar_descricao(self, descricao):
        """Processa descrição extraindo principal e observações"""
        partes = descricao.split(",")
        principal = partes[0].strip()
        observacoes = [parte.strip().replace("s/", "sem").replace("c/", "com") for parte in partes[1:]]
        observacoes_linha = ", ".join(observacoes) if observacoes else principal
        return principal, observacoes_linha
    
    def salvar_arquivo(self, alimento_json):
        """Salva dados no arquivo TXT"""
        with open(self.arquivo_path, "a", encoding='utf-8') as file:
            produto_json_str = json.dumps(alimento_json, ensure_ascii=False)
            file.write(produto_json_str + "\n")
    
    def salvar_banco(self, cursor, alimento_json):
        """Salva dados no banco PostgreSQL"""
        principal, observacoes_linha = self.processar_descricao(alimento_json['descricao'])
        
        # Inserir alimento principal
        cursor.execute("""
            INSERT INTO alimentos (codigo, classe, principal) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (codigo) DO NOTHING
            RETURNING id
        """, (alimento_json['codigo'], alimento_json['classe'], principal))
        
        result = cursor.fetchone()
        if result:
            alimento_id = result[0]
        else:
            cursor.execute("SELECT id FROM alimentos WHERE codigo = %s", 
                            (alimento_json['codigo'],))
            alimento_id = cursor.fetchone()[0]
        
        # Inserir variação
        cursor.execute("""
            INSERT INTO variacoes_alimentos (alimento_id, descricao) 
            VALUES (%s, %s) 
            RETURNING id
        """, (alimento_id, observacoes_linha))
        
        variacao_id = cursor.fetchone()[0]
        
        # Inserir nutrientes
        for nutriente in alimento_json['nutrientes']:
            cursor.execute("""
                INSERT INTO nutrientes_alimentos 
                (variacao_id, componente, unidade_medida, valor_por_100g) 
                VALUES (%s, %s, %s, %s)
            """, (
                variacao_id,
                nutriente.get('Componente', ''),
                nutriente.get('Unidades', ''),
                nutriente.get('Valor por 100g', '')
            ))

def fazer_webscraping(salvar_arquivo=True, salvar_banco=True):
    """Função principal para web scraping"""
    processor = TBCAProcessor()
    
    # Configuração inicial
    url_base = 'http://www.tbca.net.br/base-dados/composicao_alimentos.php'
    cod_alimentos = []
    parametros = {'pagina': 1}
    
    # Conexão com banco se necessário
    conn = cursor = None
    if salvar_banco:
        conn = postgresql_connection()
        cursor = conn.cursor()
    
    print("Coletando códigos dos alimentos...")
    
    # Coletar todos os códigos de alimentos
    while True:
        try:
            response = requests.get(url_base, params=parametros)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procurar links dos alimentos na página
            links_alimentos = soup.find_all('a', href=lambda x: x and 'codigo_alimento' in x)
            
            if not links_alimentos:
                break
                
            for link in links_alimentos:
                href = link.get('href')
                if 'codigo_alimento=' in href:
                    cod_alimento = href.split('codigo_alimento=')[1].split('&')[0]
                    # Extrair classe do alimento (se disponível no contexto)
                    classe_alimento = "Não especificada"
                    cod_alimentos.append((cod_alimento, classe_alimento))
            
            print(f"Página {parametros['pagina']}: {len(links_alimentos)} alimentos encontrados")
            parametros['pagina'] += 1
            
        except Exception as e:
            print(f"Erro ao processar página {parametros['pagina']}: {e}")
            break
    
    print(f"Total de alimentos coletados: {len(cod_alimentos)}")
    
    # Processar cada alimento
    for i, (cod_alimento, classe_alimento) in enumerate(cod_alimentos):
        try:
            # Fazer requisição para página individual do alimento
            url_alimento = f"{url_base}?codigo_alimento={cod_alimento}"
            response = requests.get(url_alimento)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair descrição do alimento
            descricao = "Descrição não encontrada"
            descricao_elem = soup.find('h2') or soup.find('h1') or soup.find('title')
            if descricao_elem:
                descricao = descricao_elem.get_text().strip()
            
            # Extrair tabela de nutrientes
            nutrientes = []
            tabela = soup.find('table')
            if tabela:
                linhas = tabela.find_all('tr')[1:]  # Pular cabeçalho
                for linha in linhas:
                    colunas = linha.find_all('td')
                    if len(colunas) >= 3:
                        nutriente = {
                            'Componente': colunas[0].get_text().strip(),
                            'Unidades': colunas[1].get_text().strip(),
                            'Valor por 100g': colunas[2].get_text().strip()
                        }
                        nutrientes.append(nutriente)
            
            alimento_json = {
                'codigo': cod_alimento,
                'classe': classe_alimento,
                'descricao': descricao,
                'nutrientes': nutrientes
            }
            
            if salvar_arquivo:
                processor.salvar_arquivo(alimento_json)
            
            if salvar_banco:
                processor.salvar_banco(cursor, alimento_json)
                
                # Commit periódico
                if (i + 1) % 10 == 0:
                    conn.commit()
                    print(f"Processados {i + 1} alimentos...")
                    
        except Exception as e:
            print(f"Erro ao processar {cod_alimento}: {e}")
    
    # Finalização
    if salvar_banco:
        conn.commit()
        cursor.close()
        conn.close()
    
    print("Web scraping finalizado!")

def processar_arquivo_existente():
    """Processa arquivo TXT existente para o banco"""
    processor = TBCAProcessor()
    conn = postgresql_connection()
    cursor = conn.cursor()
    
    with open(processor.arquivo_path, "r", encoding='utf-8') as file:
        for linha in file:
            if linha.strip():
                try:
                    alimento_json = json.loads(linha.strip())
                    processor.salvar_banco(cursor, alimento_json)
                except Exception as e:
                    print(f"Erro ao processar linha: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # Para fazer scraping completo
    fazer_webscraping(salvar_arquivo=True, salvar_banco=True)
    
    # Para processar apenas arquivo existente
    # processar_arquivo_existente()