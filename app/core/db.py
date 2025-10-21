import os
import psycopg
from app.core.models import Article

conn_string = os.getenv("DATABASE_URL", "")

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg.connect(conn_string)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
def close_db_connection(conn):
    """
    Closes the given database connection.
    """
    if conn:
        conn.close()

def save_article_to_db(article: Article):
    """
    Saves an article dictionary to the PostgreSQL database.
    Expects article to have keys: title, link, summary, source_name, published_at, content.
    """
    conn = get_db_connection()
    if not conn:
        print("No database connection available.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO articles (title, link, summary, source_name, published_at, content, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (link) DO NOTHING;
            """, (
            article.title,
            article.link,
            article.summary,
            article.source_name,
            article.published_at,
            article.content,
            ))
            conn.commit()
    except Exception as e:
        print(f"Error saving article to database: {e}")
    finally:
        close_db_connection(conn)