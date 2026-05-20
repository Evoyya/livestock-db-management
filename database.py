import psycopg2
from contextlib import contextmanager
from config import settings
@contextmanager
def get_connection():
    """Контекстный менеджер для автоматического закрытия коннекта."""
    conn = psycopg2.connect(settings.database_dsn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def create_tables():
    """Создание структуры таблиц (DDL)."""
    query = """
    DROP TABLE IF EXISTS livestock_population CASCADE;
    DROP TABLE IF EXISTS state_farms CASCADE;
    DROP TABLE IF EXISTS livestock_types CASCADE;

    CREATE TABLE state_farms (
        farm_code SERIAL PRIMARY KEY,
        farm_name VARCHAR(100) NOT NULL,
        district_name VARCHAR(100),
        chairman_name VARCHAR(100)
    );

    CREATE TABLE livestock_types (
        cattle_code SERIAL PRIMARY KEY,
        type_name VARCHAR(100) NOT NULL,
        breed VARCHAR(100)
    );

    CREATE TABLE livestock_population (
        farm_code INTEGER REFERENCES state_farms(farm_code) ON DELETE CASCADE,
        cattle_code INTEGER REFERENCES livestock_types(cattle_code) ON DELETE CASCADE,
        stat_date DATE NOT NULL,
        head_count INTEGER CHECK (head_count >= 0),
        PRIMARY KEY (farm_code, cattle_code, stat_date)
    );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)