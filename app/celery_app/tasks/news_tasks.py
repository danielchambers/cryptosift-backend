import json
import tornado.gen
from datetime import datetime
from app.celery_app.celery_instance import app
from app.redis.redis_instance import get_redis_client

redis_client = get_redis_client()


@tornado.gen.coroutine
def async_add(x, y):
    # Simulate an asynchronous operation
    yield tornado.gen.sleep(1)  # Wait for 1 second
    result = x + y
    raise tornado.gen.Return(result)


@app.task
def broadcast_message():
    message_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_data = {
        "message_type": "new_article",
        "message": "New article found",
        "message_date": message_date
    }
    message_json = json.dumps(message_data)
    redis_client.publish("notification_channel", message_json)
