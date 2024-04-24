import json
import tornado.gen
from celery.result import async_result
from app.celery_app.celery_instance import app
from app.redis.redis_instance import get_redis_client
from tasks.news import main

redis_client = get_redis_client()


@tornado.gen.coroutine
def async_add(x, y):
    # Simulate an asynchronous operation
    yield tornado.gen.sleep(1)  # Wait for 1 second
    result = x + y
    raise tornado.gen.Return(result)


@app.task
def broadcast_message():
    articles = async_result(main()).get()
    message_json = json.dumps(articles)
    redis_client.publish("notification_channel", message_json)
