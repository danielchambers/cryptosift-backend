import json
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
from app.redis.redis_instance import get_redis_client
from app.utils.logger import logger


class NewsHandler(tornado.websocket.WebSocketHandler):
    clients = set()
    pubsub = None

    def check_origin(self, origin):
        return True

    def open(self):
        self.clients.add(self)
        logger.info(
            f"WebSocket opened for client: {self}. Total connected clients: {len(self.clients)}"
        )

        if not self.pubsub:
            self.pubsub = get_redis_client().pubsub()
            self.pubsub.subscribe("notification_channel")
            PeriodicCallback(self.listen_for_messages, 100).start()

    def on_close(self):
        self.clients.remove(self)
        logger.info(
            f"WebSocket closed for client: {self}. Total connected clients: {len(self.clients)}"
        )

        # Unsubscribe from the Redis channel
        if self.pubsub:
            self.pubsub.unsubscribe("notification_channel")

    def on_message(self, message):
        logger.info(f"Received message from client: {self}. Message: {message}")
        # self.broadcast_to_clients(message)
        pass

    def broadcast_to_clients(self, message):
        try:
            # Decode the byte string to a regular string
            message_str = message.decode("utf-8")
            msg = json.dumps({"message": message_str})
            for client in self.clients:
                try:
                    client.write_message(msg)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {e}")
        except Exception as e:
            logger.error(f"Error decoding message: {e}")

    def listen_for_messages(self):
        if self.pubsub:
            message = self.pubsub.get_message()
            if message and message["type"] == "message":
                data = message["data"]
                logger.info(f"Received message from Redis: {data}")
                self.broadcast_to_clients(data)
