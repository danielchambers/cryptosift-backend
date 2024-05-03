import os
import re
import asyncio
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.utils.logger import logger

load_dotenv()

DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")


def log_error(logger, message, error=None):
    if error:
        logger.error(f"{message}: {str(error)}")
    else:
        logger.error(message)


ROLE_MENTION_PATTERN = re.compile(r"<@&(\d+)>")
CHANNEL_MENTION_PATTERN = re.compile(r"<#(\d+)>")
USER_MENTION_PATTERN = re.compile(r"<@(\d+)>")
EMOJI_MENTION_PATTERN = re.compile(r"<:[a-zA-Z0-9_]+:(\d+)>")


@asynccontextmanager
async def create_session():
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()


async def fetch_roles_info(guild_id, retries=3, delay=5):
    api_url = f"https://discord.com/api/v9/guilds/{guild_id}/roles"
    headers = {"Authorization": DISCORD_API_TOKEN}

    async with create_session() as session:
        for attempt in range(retries):
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        roles_info = await response.json()
                        return roles_info
                    else:
                        log_error(
                            logger,
                            f"Failed to fetch roles info for guild ID {guild_id}",
                            response.status,
                        )
            except aiohttp.ClientError as e:
                log_error(
                    logger, f"Error fetching roles info for guild ID {guild_id}", e
                )

            if attempt < retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

    log_error(
        logger,
        f"Failed to fetch roles info after {retries} attempts for guild ID {guild_id}",
    )
    return None


async def fetch_channel_info(channel_id, retries=3, delay=5):
    api_url = f"https://discord.com/api/v9/channels/{channel_id}"
    headers = {"Authorization": DISCORD_API_TOKEN}

    async with create_session() as session:
        for attempt in range(retries):
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        channel_info = await response.json()
                        return channel_info
                    else:
                        log_error(
                            logger,
                            f"Failed to fetch channel info for channel ID {channel_id}",
                            response.status,
                        )
            except aiohttp.ClientError as e:
                log_error(
                    logger,
                    f"Error fetching channel info for channel ID {channel_id}",
                    e,
                )

            if attempt < retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

    log_error(
        logger,
        f"Failed to fetch channel info after {retries} attempts for channel ID {channel_id}",
    )
    return None


def fetch_emoji_info(emoji_id):
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.webp?size=44&quality=lossless"


async def fetch_user_info(user_id, retries=3, delay=5):
    api_url = f"https://discord.com/api/v9/users/{user_id}"
    headers = {"Authorization": DISCORD_API_TOKEN}

    async with create_session() as session:
        for attempt in range(retries):
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        user_info = await response.json()
                        return user_info
                    else:
                        log_error(
                            logger,
                            f"Failed to fetch user info for user ID {user_id}",
                            response.status,
                        )
            except aiohttp.ClientError as e:
                log_error(logger, f"Error fetching user info for user ID {user_id}", e)

            if attempt < retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

    log_error(
        logger,
        f"Failed to fetch user info after {retries} attempts for user ID {user_id}",
    )
    return None


def get_discord_ids(pattern, message_text):
    ids = []
    for string in message_text.split("\n"):
        matches = pattern.findall(string)
        ids.extend(matches)
    return ids


def find_role_by_id(role_id, all_roles):
    for role in all_roles:
        if str(role["id"]) == role_id:
            return role
    return None


async def process_discord_text(server_id, text):
    role_ids = get_discord_ids(ROLE_MENTION_PATTERN, text)
    channel_ids = get_discord_ids(CHANNEL_MENTION_PATTERN, text)
    user_ids = get_discord_ids(USER_MENTION_PATTERN, text)
    emoji_ids = get_discord_ids(EMOJI_MENTION_PATTERN, text)

    tasks = []
    if emoji_ids:
        for emoji_id in emoji_ids:
            emoji_url = fetch_emoji_info(emoji_id)
            text = re.sub(
                EMOJI_MENTION_PATTERN, f'<img src="{emoji_url}" alt="emoji">', text
            )

    if user_ids:
        for user_id in user_ids:
            task = asyncio.ensure_future(fetch_user_info(user_id))
            tasks.append(task)

    if channel_ids:
        for channel_id in channel_ids:
            task = asyncio.ensure_future(fetch_channel_info(channel_id))
            tasks.append(task)

    user_infos = await asyncio.gather(*tasks, return_exceptions=True)
    for user_info in user_infos:
        if isinstance(user_info, Exception):
            log_error(logger, "Error fetching user or channel info", user_info)
        elif user_info:
            if "username" in user_info:
                user_name = user_info["username"]
                user_id = user_info["id"]
                text = text.replace(f"<@{user_id}>", f"@{user_name}")
            elif "name" in user_info:
                channel_name = user_info["name"]
                channel_id = user_info["id"]
                text = text.replace(f"<#{channel_id}>", f"#{channel_name}")

    if role_ids:
        all_roles = await fetch_roles_info(server_id)
        for role_id in role_ids:
            role = find_role_by_id(role_id, all_roles)
            if role:
                text = text.replace(f"<@&{role_id}>", f"@{role['name']}")

    return text


async def fetch_messages(
    session, server_id, channel_id, project_name, retries=3, delay=5
):
    api_url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=3"
    headers = {"Authorization": DISCORD_API_TOKEN}

    for attempt in range(retries):
        try:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    messages = await response.json()
                    return [
                        {
                            "message_id": message["id"],
                            "message_project": project_name,
                            "message_text": await process_discord_text(
                                server_id, message["content"]
                            ),
                            "message_author": message["author"]["global_name"],
                            "message_channel_id": message["channel_id"],
                            "message_server_id": message["id"],
                            "message_date": int(
                                datetime.fromisoformat(message["timestamp"]).timestamp()
                            ),
                            "message_attachments": [
                                attachment["url"].replace(" ", "")
                                for attachment in message["attachments"]
                            ],
                        }
                        for message in messages
                    ]
                else:
                    logger.warning(
                        f"Failed to fetch messages for server {server_id} and channel {channel_id}"
                    )
        except aiohttp.ClientError as e:
            logger.error(
                f"Error fetching messages for server {server_id} and channel {channel_id}, error: {e}"
            )

        if attempt < retries - 1:
            logger.info(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

    logger.error(
        f"Failed to fetch messages after {retries} attempts for server {server_id} and channel {channel_id}"
    )
    return []


async def fetch_all_messages(channels):
    async with aiohttp.ClientSession() as session:
        try:
            tasks = []
            for channel in channels:
                server_id = channel["server"]
                channel_id = channel["channel"]
                project_name = channel["project"]
                task = asyncio.ensure_future(
                    fetch_messages(session, server_id, channel_id, project_name)
                )
                tasks.append(task)

            all_messages = await asyncio.gather(*tasks)
            flattened_messages = [
                message
                for server_messages in all_messages
                for message in server_messages
            ]
            return flattened_messages
        except Exception as e:
            logger.exception(f"Error in fetch_all_messages function: {e}")
            return []


if __name__ == "__main__":
    servers = [
        {
            "server": "816779565796032513",
            "channels": ["834798371872047125"],
            "project": "Indiego",
        },
        {
            "server": "850372362033430539",
            "channels": ["860121140827127848"],
            "project": "Meld",
        },
        {
            "server": "837215135999197246",
            "channels": ["846654998096117791"],
            "project": "Iagon",
        },
        {
            "server": "903302807346630656",
            "channels": ["903853505356386384"],
            "project": "Hosky",
        },
        {
            "server": "915937361286795334",
            "channels": ["915937634143043694"],
            "project": "Wingriders",
        },
    ]
    channels = [
        {"server": server["server"], "channel": channel, "project": server["project"]}
        for server in servers
        for channel in server["channels"]
    ]
    messages = asyncio.run(fetch_all_messages(channels))
    print(messages)
