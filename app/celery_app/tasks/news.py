import asyncio
import aiohttp
import feedparser
import time
from datetime import datetime
from app.utils.logger import logger


async def download_feed(session, url, retries=3, delay=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    return feedparser.parse(content)
                else:
                    logger.warning(
                        f"Failed to download feed (status code {response.status}): {url}"
                    )
        except aiohttp.ClientError as e:
            logger.error(f"Error downloading feed: {url}, error: {e}")

        if attempt < retries - 1:
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    logger.error(f"Failed to download feed after {retries} attempts: {url}")
    return None


def extract_author(entry):
    author = entry.get("author")
    if author:
        return author
    logger.warning("No author information found")
    return "No author information found"


def extract_image(entry):
    try:
        if "media_content" in entry:
            return entry["media_content"][0]["url"]
        elif "enclosures" in entry and entry.enclosures:
            return entry.enclosures[0].get("href")
    except (KeyError, IndexError) as e:
        logger.error(f"Error extracting image: {e}")
    return "no_image"


def extract_published(entry):
    try:
        published = entry.get("published", "")
        date_object = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
        timestamp = int(date_object.timestamp())
        return timestamp
    except Exception as e:
        logger.error(f"Error extracting published: {e}")
    return "No published date found"


def process_entry(entry):
    try:
        article = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "description": entry.get("description", ""),
            "published": extract_published(entry),
            "author": extract_author(entry),
            "image": extract_image(entry),
        }
        return article
    except Exception as e:
        logger.exception(f"Error processing entry: {e}")
        return None


async def process_feed_entries(feed):
    articles = []
    try:
        for entry in feed.entries:
            article = process_entry(entry)
            if article:
                articles.append(article)
    except Exception as e:
        logger.exception(f"Error processing feed entries: {e}")
    return articles


async def main():
    feed_urls = [
        # image in media_content
        # "https://newsbtc.com/analysis/ada/feed/",
        # "https://newsbtc.com/news/cardano/feed/",
        # "https://cointelegraph.com/rss/tag/cardano/",
        # "https://coindesk.com/arc/outboundfeeds/rss/",
        # "https://cryptonews.com/news/feed/",
        # "https://cryptoslate.com/news/cardano/feed/",
        # "https://beincrypto.com/feed/",
        # "https://crypto.news/feed/",
        # "https://bitcoinist.com/feed/",
        # "https://cryptopotato.com/feed/",
        # "https://cryptobriefing.com/feed/",
        # image possibly in description
        "https://dailyhodl.com/feed/",
        # "https://news.bitcoin.com/feed/",
        # "https://forkast.news/feed/",
        # "https://dailycoin.com/cardano-ada/feed/",
        # "https://ambcrypto.com/feed/",
        # "https://zycrypto.com/tag/cardano/feed/",
        # "https://zycrypto.com/tag/adausd/feed/",
        # "https://zycrypto.com/tag/ada/feed/",
        # "https://cryptoglobe.com/rss/feed.xml",
        # "https://watcher.guru/news/category/cardano/feed/",
    ]

    async with aiohttp.ClientSession() as session:
        try:
            feeds = await asyncio.gather(
                *(download_feed(session, url) for url in feed_urls)
            )

            all_articles = []
            for feed in feeds:
                if feed is not None:
                    articles = await process_feed_entries(feed)
                    all_articles.extend(articles)

            return all_articles
        except Exception as e:
            logger.exception(f"Error in main function: {e}")
            return []


if __name__ == "__main__":
    articles = asyncio.run(main())
    print(articles)
