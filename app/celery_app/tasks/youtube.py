import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from app.utils.logger import logger

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


@asynccontextmanager
async def create_session() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()


async def search_videos(
    keyword: str, event_type: str, max_results: int, order: str
) -> List[str]:
    """
    Search for videos on YouTube based on the provided parameters.
    :param keyword: The search keyword.
    :param event_type: The event type to filter the search results.
    :param max_results: The maximum number of results to retrieve.
    :param order: The order of the search results.
    :return: A list of video IDs matching the search criteria.
    """
    try:
        async with create_session() as session:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "q": keyword,
                "type": "video",
                "eventType": event_type,
                "part": "id,snippet",
                "maxResults": max_results,
                "order": order,
                "key": YOUTUBE_API_KEY,
            }
            async with session.get(url, params=params) as response:
                search_response = await response.json()
                videos = [
                    search_result["id"]["videoId"]
                    for search_result in search_response.get("items", [])
                ]
                return videos
    except Exception as e:
        logger.error(f"An error occurred during video search: {str(e)}")
        return []


async def get_video_data(video_results: List[str]) -> List[Dict[str, Any]]:
    """
    Retrieve detailed information for the given video IDs.
    :param video_results: A list of video IDs.
    :return: A list of dictionaries containing video data.
    """
    video_data = []
    async with create_session() as session:
        tasks = []
        for video_id in video_results:
            task = asyncio.ensure_future(fetch_video_data(session, video_id))
            tasks.append(task)
        video_data = await asyncio.gather(*tasks)
    return video_data


async def fetch_video_data(
    session: aiohttp.ClientSession, video_id: str
) -> Dict[str, Any]:
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "id": video_id,
            "key": YOUTUBE_API_KEY,
        }
        async with session.get(url, params=params) as response:
            video_response = await response.json()
            if video_response["items"]:
                item = video_response["items"][0]
                return {
                    "id": item["id"],
                    "title": item["snippet"]["title"],
                    "full_description": item["snippet"]["description"],
                    "channel_title": item["snippet"]["channelTitle"],
                    "published_at": item["snippet"]["publishedAt"],
                    "urls": {
                        "channel": f"https://www.youtube.com/@{item['snippet']['channelTitle']}",
                        "video": f"https://www.youtube.com/watch?v={item['id']}",
                    },
                }
            else:
                logger.warning(f"Video with ID {video_id} not found.")
    except Exception as e:
        logger.error(
            f"An error occurred while retrieving video data for ID {video_id}: {str(e)}"
        )


async def main() -> None:
    keywords = ["cardano", "singularity net", "hoskinson"]
    event_type = "completed"
    max_results = 1
    order = "date"
    all_videos = []
    for keyword in keywords:
        videos = await search_videos(keyword, event_type, max_results, order)
        videos_data = await get_video_data(videos)
        all_videos.extend(videos_data)
    logger.info(all_videos)


if __name__ == "__main__":
    asyncio.run(main())
