import asyncio
import aiohttp
import feedparser


async def download_feed(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            content = await response.text()
            return feedparser.parse(content)
        else:
            print(f"Failed to download feed: {url}")
            return None


def extract_author(entry):
    author = entry.get("author")
    if author:
        return author

    authors = entry.get("authors")
    if authors:
        return ", ".join(author.get("name", "") for author in authors)

    return "No author information found"


def extract_image(entry):
    if "media_thumbnail" in entry:
        return entry["media_thumbnail"][0]["url"]
    elif "media_content" in entry:
        return entry["media_content"][0]["url"]
    elif "enclosures" in entry:
        enclosure_url = entry.enclosures[0].get("href", "")
        if enclosure_url.endswith((".jpg", ".jpeg", ".png", ".gif")):
            return enclosure_url

    return "No image found"


def print_entry_details(entry):
    title = entry.get("title", "")
    link = entry.get("link", "")
    summary = entry.get("summary", "")
    description = entry.get("description", "")
    published = entry.get("published", "")

    print(f"Title: {title}\n")
    print(f"Link: {link}\n")
    print(f"Summary: {summary if summary == description else summary + description}\n")
    print(f"Published: {published}\n")
    print(f"Author: {extract_author(entry)}")
    print(f"Image: {extract_image(entry)}")
    print("\n\n")


async def process_feed_entry(entry):
    print_entry_details(entry)


async def main():
    feed_urls = [
        "https://www.newsbtc.com/tag/ada/feed/",
        # ... add more feed URLs ...
    ]

    async with aiohttp.ClientSession() as session:
        feeds = await asyncio.gather(
            *(download_feed(session, url) for url in feed_urls)
        )

        entries = [entry for feed in feeds if feed for entry in feed.entries]
        await asyncio.gather(*(process_feed_entry(entry) for entry in entries))


if __name__ == "__main__":
    asyncio.run(main())
