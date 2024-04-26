import re
import time
import aiohttp
import asyncio
import feedparser
from datetime import datetime
from urllib.parse import urlparse
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


def process_entry(entry, keywords=None):
    try:
        link = entry.get("link", "")
        parsed_url = urlparse(link)
        hostname_parts = parsed_url.hostname.split(".")
        organization = ".".join(hostname_parts[-2:])

        article = {
            "organization": organization,
            "title": entry.get("title", ""),
            "link": link,
            "description": entry.get("description", ""),
            "published": extract_published(entry),
            "author": extract_author(entry),
            "image": extract_image(entry),
        }

        # Check if any of the keywords are present in the title or description as whole words
        if keywords:
            if any(
                re.search(r"\b" + re.escape(keyword.lower()) + r"\b", article["title"].lower())
                or re.search(r"\b" + re.escape(keyword.lower()) + r"\b", article["description"].lower())
                for keyword in keywords
            ):
                return article
            else:
                return None
        else:
            return article
    except Exception as e:
        logger.exception(f"Error processing entry: {e}")
        return None


async def process_feed_entries(feed, keywords=None):
    articles = []
    try:
        for entry in feed.entries:
            article = process_entry(entry, keywords)
            if article:
                articles.append(article)
    except Exception as e:
        logger.exception(f"Error processing feed entries: {e}")
    return articles


async def fetch_and_filter_articles(feed_urls, keywords=None):
    async with aiohttp.ClientSession() as session:
        try:
            feeds = await asyncio.gather(
                *(download_feed(session, url) for url in feed_urls)
            )

            all_articles = []
            for feed in feeds:
                if feed is not None:
                    articles = await process_feed_entries(feed, keywords)
                    all_articles.extend(articles)

            return all_articles
        except Exception as e:
            logger.exception(f"Error in fetch_and_filter_articles function: {e}")
            return []


if __name__ == "__main__":
    feed_urls = [
        # "https://cointelegraph.com/rss/tag/cardano/",
        "https://coindesk.com/arc/outboundfeeds/rss/",
    ]
    keywords = ["cardano", "hoskinson", "ada", "iohk", "iog", "$ada"]
    articles = asyncio.run(fetch_and_filter_articles(feed_urls, keywords))
    print(articles)
