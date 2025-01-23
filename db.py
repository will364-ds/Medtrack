import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="medtrack",
            user="postgres",
            password="password",
            host="localhost",
            port=5432,
            cursor_factory=RealDictCursor  # Retorna resultados como dicionários
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
