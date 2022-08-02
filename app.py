import os

from flask import Flask, abort, request
from redis import Redis

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", "6379")

app = Flask(__name__)
r = Redis(host=redis_host, port=int(redis_port))

app.logger.info(f"REDIS_HOST = {redis_host}")
app.logger.info(f"REDIS_PORT = {redis_port}")


@app.get("/")
def hello_world():
    return "<p>Hello World!</p>"


@app.get("/<key>")
def get_by_key(key: str):
    value = r.get(key)
    if value:
        return value
    else:
        abort(404)


@app.put("/<key>")
def set_by_key(key: str):
    r.set(key, request.form["data"])
    return ("", 204)
