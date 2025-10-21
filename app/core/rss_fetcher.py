from concurrent.futures.thread import ThreadPoolExecutor
from typing_extensions import LiteralString
import feedparser
import logging
import trafilatura
import requests
from app.core.cleaner_graph import build_graph, ArticleState
from pydantic import BaseModel
from app.core.db import save_article_to_db
from app.core.models import Article
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "ET": "https://bfsi.economictimes.indiatimes.com/rss/lateststories"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/128.0.0.0 Safari/537.36"
}

# Create a single session and configure pool
session = requests.Session()
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update(HEADERS)

def fetch_article_content(url: str, session: requests.Session) -> str:
    """Extracts full article text using trafilatura with a shared session."""
    try:
        downloaded = session.get(url, timeout=10).text
        if not downloaded:
            resp = session.get(url, timeout=10)
            downloaded = resp.text if resp.status_code == 200 else None

        text = trafilatura.extract(downloaded)
        if text:
            return text.strip()
        else:
            logger.warning(f"❌ No content extracted for {url}")
            return ""
    except Exception as e:
        logger.warning(f"⚠️ Error extracting {url}: {e}")
        return ""


def fetch_feeds() -> list[Article]:
    """Fetch all feeds concurrently using a single shared pool and session."""
    articles: list[Article] = []
    all_tasks = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        for name, url in RSS_FEEDS.items():
            feed = feedparser.parse(url)
            for entry in feed.entries:
                all_tasks.append((name, entry))

        # Run downloads concurrently
        futures = [executor.submit(fetch_article_content, entry.link, session) for _, entry in all_tasks]

        for (name, entry), future in zip(all_tasks, futures):
            content = future.result()
            articles.append(
                Article(
                    title=entry.title,  # type: ignore
                    link=entry.link,  # type: ignore
                    summary=entry.get("summary", ""),  # type: ignore
                    source_name=name,
                    published_at=entry.get("published", ""),  # type: ignore
                    content=content,
                )
            )

    logger.info(f"✅ Fetched {len(articles)} articles from {len(RSS_FEEDS)} sources.")
    return articles

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    articles = fetch_feeds()
    logger.info(f"✅ Fetched {len(articles)} articles, saving to DB.")
    for article in articles:
        if article.content:
            save_article_to_db(article)
    # content = fetch_article_content(url='https://bfsi.economictimes.indiatimes.com/articles/sbi-investing-in-technology-for-high-availability-of-digital-channels/124378704')
    # graph = build_graph()
    # state = graph.invoke(ArticleState(text=content, cleaned_text="", summary=""))
    # print(state['cleaned_text'])