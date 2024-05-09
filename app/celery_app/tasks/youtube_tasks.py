import json
import asyncio
from app.celery_app.celery_instance import app
from app.redis.redis_instance import get_redis_client
from .youtube import fetch_youtube_data

redis_client = get_redis_client()


@app.task
def broadcast_youtube_data():
    keywords = ["cardano", "singularity net", "hoskinson"]
    max_results = 3
    messages = asyncio.run(fetch_youtube_data(keywords, max_results))
    message_json = json.dumps(messages)
    redis_client.publish("notification_channel", message_json)
