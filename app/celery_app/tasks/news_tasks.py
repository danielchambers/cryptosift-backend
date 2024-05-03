import json
import asyncio
from app.celery_app.celery_instance import app
from app.redis.redis_instance import get_redis_client
from .news import fetch_news_data

redis_client = get_redis_client()


@app.task
def broadcast_news_data():
    cardano_feed_urls = [
        "https://newsbtc.com/analysis/ada/feed/",
        "https://newsbtc.com/news/cardano/feed/",
        "https://cointelegraph.com/rss/tag/cardano/",
        "https://cryptoslate.com/news/cardano/feed/",
        "https://dailycoin.com/cardano-ada/feed/",
        "https://zycrypto.com/tag/cardano/feed/",
        "https://zycrypto.com/tag/adausd/feed/",
        "https://zycrypto.com/tag/ada/feed/",
        "https://watcher.guru/news/category/cardano/feed/",
    ]
    generic_feed_urls = [
        "https://coindesk.com/arc/outboundfeeds/rss/",
        "https://cryptonews.com/news/feed/",
        "https://beincrypto.com/feed/",
        "https://crypto.news/feed/",
        "https://bitcoinist.com/feed/",
        "https://cryptopotato.com/feed/",
        "https://cryptobriefing.com/feed/",
        "https://dailyhodl.com/feed/",
        "https://news.bitcoin.com/feed/",
        "https://forkast.news/feed/",
        "https://ambcrypto.com/feed/",
        "https://cryptoglobe.com/rss/feed.xml",
    ]
    cardano_keywords = ["cardano", "hoskinson", "ada", "iohk", "iog", "$ada"]
    cardano_feeds = asyncio.run(fetch_news_data(cardano_feed_urls, []))
    generic_feeds = asyncio.run(fetch_news_data(generic_feed_urls, cardano_keywords))
    combined_articles = cardano_feeds + generic_feeds
    message_json = json.dumps(combined_articles)
    redis_client.publish("notification_channel", message_json)
