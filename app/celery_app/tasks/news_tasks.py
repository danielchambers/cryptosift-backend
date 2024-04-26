import json
import asyncio
import tornado.gen
from app.celery_app.celery_instance import app
from app.redis.redis_instance import get_redis_client
from .news import fetch_and_filter_articles

redis_client = get_redis_client()


@tornado.gen.coroutine
def async_add(x, y):
    # Simulate an asynchronous operation
    yield tornado.gen.sleep(1)  # Wait for 1 second
    result = x + y
    raise tornado.gen.Return(result)


@app.task
def broadcast_message():
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

    cardano_feed_articles = asyncio.run(fetch_and_filter_articles(cardano_feed_urls, []))
    generic_feed_articles = asyncio.run(fetch_and_filter_articles(generic_feed_urls, cardano_keywords))

    combined_articles = cardano_feed_articles + generic_feed_articles

    message_json = json.dumps(combined_articles)
    redis_client.publish("notification_channel", message_json)
