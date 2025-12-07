import os
from typing import Iterator, cast, Dict, Any
import psycopg
from pydantic import ValidationError
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

def make_article_processed(article: Article):
    conn = get_db_connection()
    if not conn:
        print("No database connection available.")
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE articles SET processed = true WHERE id = %s", (article.id,))
        conn.commit()
    
def get_unprocessed_articles(batch_size: int = 50) -> Iterator[Article]:
    conn = get_db_connection()
    if not conn:
        return
    with conn:
        with conn.cursor(name="unprocessed_articles_cursor") as cur:
            cur.itersize = batch_size
            cur.execute("SELECT id, title, link, summary, source_name, published_at, content FROM articles WHERE processed = false ORDER BY id")
            for row in cur:
                article_data = cast(Dict[str, Any], row)
                try:
                    yield Article(**article_data)
                except ValidationError as ve:
                    print(f"Data validation error for article ID {article_data.get('id')}: {ve}")