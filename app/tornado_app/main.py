import os
from dotenv import load_dotenv

import tornado.web
import tornado.ioloop

from app.tornado_app.handlers.main_handler import MainHandler
from app.tornado_app.handlers.news_handler import NewsHandler

# Load environment variables from .env file
load_dotenv()

# Get the debug value from the environment variable
DEBUG = os.environ.get("TORNADO_DEBUG")
PORT = os.environ.get("TORNADO_PORT", 8000)


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/news", NewsHandler),
        ],
        debug=DEBUG,
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(int(PORT))
    print("Tornado app listening on http://localhost:8000")
    tornado.ioloop.IOLoop.current().start()
