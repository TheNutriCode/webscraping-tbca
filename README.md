# Brazilian Food Composition Table - Web Scraping

This project performs web scraping of the Brazilian Food Composition Table (TBCA) and stores the nutritional data of more than 5,500 foods in a PostgreSQL database and a JSON file, making it easy to use by applications and systems.

## Project Structure

```
├── src/                    # Python source code
│   ├── webscraping.py      # Main webscraping and processing script
│   ├── dbconnect.py        # PostgreSQL connection configuration
│   ├── requirements.txt    # Python dependencies
│   └── modeling.png       # Database modeling diagram
├── docker/                 # Docker configurations
│   ├── docker-compose.yml  # Container orchestration
│   ├── Dockerfile          # Webscraper image
│   └── scripts/
│       └── create_database.sql  # Database creation script
├── data/                   # Generated data files (created automatically)
└── .env.example            # Example of environment variables
```

## Features

- 🕷️ **Web Scraping** of the official TBCA website
- 💾 **Dual storage**: PostgreSQL + JSON file
- 🐳 **Containerization** with Docker and Docker Compose
- 📊 **Relational database** with 3 normalized tables
- 🔄 **Incremental processing** with duplicate control
- 📈 **Progress monitoring** during collection

## Database Modeling

The project uses a relational structure with 3 tables:

- **`foods`**: Basic information (code, class, main name)
- **`food_variations`**: Variations and detailed descriptions
- **`food_nutrients`**: Nutritional values per variation

See `src/modeling.png` for the complete database diagram.

## Configuration and Execution

### Option 1: Docker (Recommended) 🐳

**Prerequisites**: Docker and Docker Compose

```powershell
# Clone the repository
git clone <your-repo>
cd webscraping-tbca

# Run full webscraping
cd docker
docker-compose up --build
```

**Available services:**

- **PostgreSQL**: `localhost:5432` (tbca_db/postgres/postgres)
- **WebScraper**: Automatically runs the scraping

### Option 2: Local Execution

**Prerequisites**: Python 3.8+, PostgreSQL installed

#### 1. Configure PostgreSQL

```sql
-- Connect as postgres superuser
CREATE DATABASE tbca_db;
```

#### 2. Configure Python environment

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r src\requirements.txt
```

#### 3. Configure environment variables

Copy `.env.example` to `.env` and configure:

```env
DB_HOST=localhost
DB_NAME=tbca_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

#### 4. Run webscraping

```powershell
cd src
python webscraping.py
```

## How to Use

### Full Scraping (default)

```python
# Saves to PostgreSQL + JSON file
run_webscraping(save_to_file=True, save_to_db=True)

# Only PostgreSQL
run_webscraping(save_to_file=False, save_to_db=True)

# Only JSON file
run_webscraping(save_to_file=True, save_to_db=False)
```

### Process Existing File

```python
# Processes data/foods.txt file to the database
process_existing_file()
```

## Data Structure

### JSON File (data/foods.txt)

```json
{
  "code": "C0001",
  "class": "Cereals",
  "description": "Rice, brown, cooked",
  "nutrients": [
    {
      "Component": "Energy",
      "Units": "kcal",
      "Value per 100g": "123"
    }
  ]
}
```

### PostgreSQL Database

- **foods**: `id`, `code`, `class`, `main`, `created_at`
- **food_variations**: `id`, `food_id`, `description`, `created_at`
- **food_nutrients**: `id`, `variation_id`, `component`, `unit_of_measurement`, `value_per_100g`, `created_at`

## Technologies

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-latest-blue)](https://www.docker.com/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12.2-brightgreen)](https://pypi.org/project/beautifulsoup4/)
[![Requests](https://img.shields.io/badge/Requests-2.31.0-brightgreen)](https://pypi.org/project/requests/)
[![Psycopg2](https://img.shields.io/badge/Psycopg2-2.9.7-brightgreen)](https://pypi.org/project/psycopg2/)

## Contribution

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

This project is under the MIT license. See the [LICENSE](LICENSE) file for more details.

## Data Usage

The `data/foods.txt` file contains nutritional data in JSON format. The data can be easily imported and used in nutrition applications, food recommendation systems, or academic research.

**Source**: [Brazilian Food Composition Table (TBCA)](http://www.tbca.net.br/)