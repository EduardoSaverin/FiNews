from app.core.rss_fetcher import fetch_feeds
from app.core.db import save_article_to_db, make_article_processed, get_unprocessed_articles
from app.celery_app import app
from app.core.cleaner_graph import build_graph, ArticleState

@app.task
def fetch_and_process_articles():
    articles = fetch_feeds()
    for article in articles:
        save_article_to_db(article)
    return f"Processed {len(articles)} articles."

@app.task
def clean_articles():
    graph = build_graph()
    unprocessed_articles = get_unprocessed_articles()
    for article in unprocessed_articles:
        state = graph.invoke(ArticleState(text=article.content, cleaned_text="", summary=""))
        article.content = state['cleaned_text']
        make_article_processed(article)