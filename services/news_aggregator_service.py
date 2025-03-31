import time
from urllib.parse import urlparse
import feedparser
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from requests_html import HTMLSession

from core.database import get_db
from models.news import NewsArticle
from core.logger import logger
from services.sentiment_analysis_service import analyze_sentiment
from services.summarization_service import generate_summary

RSS_FEEDS = [
    # "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^DJI,^GSPC,^IXIC&region=US&lang=en-US",    # Yahoo Finance
    # "https://www.investing.com/rss/news.rss",                                                      # Investing.com
    "https://news.google.com/rss/search?q=finance+news&hl=en-US&gl=US&ceid=US:en"                  # Google Finance
]

MAX_RETRIES = 5
BACKOFF_FACTOR = 2

def fetch_rss_feeds():
    """Fetch articles from multiple RSS feeds."""
    logger.info("Fetching financial news from RSS feeds...")
    all_articles = []

    for feed_url in RSS_FEEDS:
        logger.info(f"Fetching feed: {feed_url}")

        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                logger.warning(f"No articles found in feed: {feed_url}")
                continue

            for entry in feed.entries[:5]:
                logger.info(f"Entry: {entry}")
                article = {
                    "title": entry.title,
                    "url": entry.link,
                    "source": urlparse(feed_url).netloc,
                    "published_at": datetime(*entry.published_parsed[:6])
                }
                all_articles.append(article)
            
        except Exception as e:
            logger.error(f"Error processing the feed {feed_url}: {str(e)}")
    logger.info(f"Fetched total {len(all_articles)} articles")
    return all_articles

def retry_request(url, max_retries=MAX_RETRIES, backoff=BACKOFF_FACTOR, timeout=10):
    """Performs a GET request with retries and exponential backoff."""
    for attempt in range(1, max_retries+1):
        try:
            response = requests.get(url, timeout=timeout)

            if response.status_code == 200:
                return response
            
            logger.warning(f"Attempt: {attempt}/{max_retries}: Failed to fetch {url} (Status: {response.status_code})")
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            logger.error(f"Attempt {attempt}/{max_retries} failed for {url}. Error: {str(e)}")
        time.sleep(backoff ** attempt)
    
    logger.error(f"Max reties reached for {url}. Failed to fetch")
    return None

# For handling Google News links properly
def resolve_google_news_redirect(url):
    try:
        session = requests.Session()
        response = session.get(url, allow_redirects=False)
        logger.info(f"Response headers: {response.headers}")
        if response.status_code in (301, 302):
            return response.headers['Location']
        return url
    except Exception as e:
        logger.error(f"Failed to resolve redirect: {str(e)}")
        return url

def extract_article_content(article_url: str):
    """Extracts the main content of the article using BeautifulSoup with retries and error handling."""
    try:
        logger.info(f"Extracting content from {article_url}")

        # response = retry_request(article_url)
        if "news.google.com" in article_url:
            article_url = resolve_google_news_redirect(article_url)
            logger.info(f"Resolved to: {article_url}")

        session = HTMLSession()
        response = session.get(article_url)
        response.html.render(timeout=20) 

        if response is None:
            logger.warning(f"Skipping the article due to failures: {article_url}")
            return ""
        
        content = ""
        
        # Try common article container selectors
        article_containers = response.html.find('article') or \
                            response.html.find('.article-body') or \
                            response.html.find('.article-content') or \
                            response.html.find('#article-body')
        
        if article_containers:
            content = article_containers[0].text
        else:
            # Fallback to paragraphs
            paragraphs = response.html.find('p')
            content = " ".join(p.text for p in paragraphs)

        # logger.info(f"Content for {article_url}: {response.content}")
        # soup = BeautifulSoup(response.content, "html.parser")

        # paragraphs = soup.find_all('p')
        # if not paragraphs:
        #     logger.warning(f"No <p> tags found. Trying <div> extraction...")
        #     paragraphs = soup.find_all('div')

        # content = " ".join(p.get_text() for p in paragraphs)

        if not content.strip():
            logger.warning(f"No content found for {article_url}.")
            return "No content available."
        
        logger.info(f"Fetched content for {article_url}: {content[:30]}...")
        content = content[:3000]

        return content
    except Exception as e:
        logger.error(f"Failed to extract content from {article_url}: {str(e)}")
        return ""

def store_articles_db(articles: list, db: Session):
    """Store the fetched articles in PostgreSQL"""
    logger.info("Storing articles in PostgreSQL...")

    stored_count = 0
    for article in articles:
        try:
            existing_article = db.query(NewsArticle).filter(NewsArticle.url == article['url']).first()

            if existing_article:
                logger.info(f"Skipping duplicate: {article['title']}")
                continue

            content = extract_article_content(article['url'])
            summary = generate_summary(content)
            sentiment = analyze_sentiment(summary)

            news_article = NewsArticle(
                title=article['title'],
                source=article['source'],
                url=article['url'],
                published_at=article['published_at'],
                summary=summary,
                sentiment=sentiment
            )

            db.add(news_article)
            stored_count += 1
        except Exception as e:
            logger.error(f"Failed to store article {article['title']}: {str(e)}")
    
    db.commit()
    logger.info(f"{stored_count} articles added to Postgres")

def run_news_aggregator():
    """Run the complete News aggregation flow"""
    logger.info("Starting news aggregation")
    try:
        articles = fetch_rss_feeds()
        if not articles:
            logger.warning(f"No new articles fetched. Exiting.")
            return
        
        db = next(get_db())
        store_articles_db(articles, db)

        logger.info("News aggregation completed")
    except Exception as e:
        logger.error(f"News aggregation failed: {str(e)}")

if __name__ == "__main__":
    run_news_aggregator()