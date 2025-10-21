from celery import Celery
from app.core.rss_fetcher import fetch_feeds
from app.core.db import save_article_to_db
import os
from app.celery_app import app

@app.task
def fetch_and_process_articles():
    articles = fetch_feeds()
    for article in articles:
        save_article_to_db(article)
    return f"Processed {len(articles)} articles."