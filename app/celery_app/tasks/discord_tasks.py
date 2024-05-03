import json
import asyncio
from app.celery_app.celery_instance import app
from app.redis.redis_instance import get_redis_client
from .discord import fetch_discord_data

redis_client = get_redis_client()


@app.task
def broadcast_discord_message():
    servers = [
        {
            "project": "Indiego",
            "server": "816779565796032513",
            "channels": ["834798371872047125"],
        },
        {
            "project": "Meld",
            "server": "850372362033430539",
            "channels": ["860121140827127848"],
        },
        {
            "project": "Iagon",
            "server": "837215135999197246",
            "channels": ["846654998096117791"],
        },
        {
            "project": "Hosky",
            "server": "903302807346630656",
            "channels": ["903853505356386384"],
        },
        {
            "project": "Wingriders",
            "server": "915937361286795334",
            "channels": ["915937634143043694"],
        },
    ]
    channels = [
        {"server": server["server"], "channel": channel, "project": server["project"]}
        for server in servers
        for channel in server["channels"]
    ]
    messages = asyncio.run(fetch_discord_data(channels))
    message_json = json.dumps(messages)
    redis_client.publish("notification_channel", message_json)
