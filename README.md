# Tabela Brasileira de Composição de Alimentos - Web Scraping

Este projeto realiza web scraping da Tabela Brasileira de Composição de Alimentos (TBCA) e armazena os dados nutricionais de mais de 5.500 alimentos em um banco PostgreSQL e arquivo JSON, facilitando o uso por aplicações e sistemas.

## Estrutura do Projeto

```
├── src/                    # Código fonte Python
│   ├── webscrapping.py     # Script principal de webscraping e processamento
│   ├── dbconnect.py        # Configuração de conexão com PostgreSQL
│   ├── requirements.txt   # Dependências Python
│   └── modelagem.png      # Diagrama da modelagem do banco
├── docker/                # Configurações Docker
│   ├── docker-compose.yml # Orquestração dos containers
│   ├── Dockerfile         # Imagem do webscraper
│   └── scripts/
│       └── create_database.sql  # Script de criação do banco
├── data/                  # Arquivos de dados gerados (criado automaticamente)
└── .env.example          # Exemplo de variáveis de ambiente
```

## Funcionalidades

- 🕷️ **Web Scraping** do site oficial da TBCA
- 💾 **Armazenamento duplo**: PostgreSQL + arquivo JSON
- 🐳 **Containerização** com Docker e Docker Compose
- 📊 **Banco relacional** com 3 tabelas normalizadas
- 🔄 **Processamento incremental** com controle de duplicatas
- 📈 **Monitoramento** de progresso durante a coleta

## Modelagem do Banco de Dados

O projeto utiliza uma estrutura relacional com 3 tabelas:

- **`alimentos`**: Informações básicas (código, classe, nome principal)
- **`variacoes_alimentos`**: Variações e descrições detalhadas
- **`nutrientes_alimentos`**: Valores nutricionais por variação

Ver `src/modelagem.png` para o diagrama completo do banco.

## Configuração e Execução

### Opção 1: Docker (Recomendado) 🐳

**Pré-requisitos**: Docker e Docker Compose

```powershell
# Clonar o repositório
git clone <seu-repo>
cd webscraping-tbca

# Executar webscraping completo
cd docker
docker-compose up --build
```

**Serviços disponíveis:**

- **PostgreSQL**: `localhost:5432` (tbca_db/postgres/postgres)
- **WebScraper**: Executa automaticamente o scraping

### Opção 2: Execução Local

**Pré-requisitos**: Python 3.8+, PostgreSQL instalado

#### 1. Configurar PostgreSQL

```sql
-- Conectar como superusuário postgres
CREATE DATABASE tbca_db;
```

#### 2. Configurar ambiente Python

```powershell
# Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r src\requirements.txt
```

#### 3. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e configure:

```env
DB_HOST=localhost
DB_NAME=tbca_db
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_PORT=5432
```

#### 4. Executar o webscraping

```powershell
cd src
python webscrapping.py
```

## Como Usar

### Scraping Completo (padrão)

```python
# Salva em PostgreSQL + arquivo JSON
fazer_webscraping(salvar_arquivo=True, salvar_banco=True)

# Apenas PostgreSQL
fazer_webscraping(salvar_arquivo=False, salvar_banco=True)

# Apenas arquivo JSON
fazer_webscraping(salvar_arquivo=True, salvar_banco=False)
```

### Processar Arquivo Existente

```python
# Processa arquivo data/alimentos.txt para o banco
processar_arquivo_existente()
```

## Estrutura dos Dados

### Arquivo JSON (data/alimentos.txt)

```json
{
  "codigo": "C0001",
  "classe": "Cereais",
  "descricao": "Arroz, integral, cozido",
  "nutrientes": [
    {
      "Componente": "Energia",
      "Unidades": "kcal",
      "Valor por 100g": "123"
    }
  ]
}
```

### Banco PostgreSQL

- **alimentos**: `id`, `codigo`, `classe`, `principal`, `created_at`
- **variacoes_alimentos**: `id`, `alimento_id`, `descricao`, `created_at`
- **nutrientes_alimentos**: `id`, `variacao_id`, `componente`, `unidade_medida`, `valor_por_100g`, `created_at`

## Tecnologias

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-latest-blue)](https://www.docker.com/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12.2-brightgreen)](https://pypi.org/project/beautifulsoup4/)
[![Requests](https://img.shields.io/badge/Requests-2.31.0-brightgreen)](https://pypi.org/project/requests/)
[![Psycopg2](https://img.shields.io/badge/Psycopg2-2.9.7-brightgreen)](https://pypi.org/project/psycopg2/)

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Uso dos Dados

O arquivo `data/alimentos.txt` contém os dados nutricionais em formato JSON. Os dados podem ser facilmente importados e utilizados em aplicações de nutrição, sistemas de recomendação alimentar, ou pesquisas acadêmicas.

**Fonte**: [Tabela Brasileira de Composição de Alimentos (TBCA)](http://www.tbca.net.br/)
