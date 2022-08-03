import logging
import os

import strawberry
from fastapi import FastAPI
from redis import Redis
from strawberry.fastapi import GraphQLRouter

logger = logging.getLogger("uvicorn")

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", "6379")

redis_client = Redis(
    host=redis_host, port=int(redis_port), decode_responses=True)

logger.info(f"REDIS_HOST = {redis_host}")
logger.info(f"REDIS_PORT = {redis_port}")


@strawberry.type
class KeyValue:
    key: str
    value: str


@strawberry.type
class KeyNotFoundError:
    key: str


Response = strawberry.union("QueryResponse", (KeyValue, KeyNotFoundError))


@strawberry.type
class Query:
    @strawberry.field
    def get_by_key(key: str) -> Response:
        value = redis_client.get(key)
        if value:
            return KeyValue(key=key, value=value)
        else:
            return KeyNotFoundError(key=key)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def set_by_key(self, key: str, value: str) -> KeyValue:
        redis_client.set(key, value)
        return KeyValue(key=key, value=value)


schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
