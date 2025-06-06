import asyncio
from typing import Optional, List

import redis.asyncio as redis
import orjson

from app.config import settings


class RedisMemory:
    def __init__(self, url=settings.REDIS_DATABASE_URL, ttl=settings.REDIS_MEMORY_TTL):
        self.redis = redis.from_url(url, encoding="utf-8", decode_responses=True)
        self.ttl = ttl
        self.memory_key = settings.SHORT_MEMORY_DB_NAME  # 总表 key

    async def check_filed(self, user_id: str) -> bool:
        val = await self.redis.get(user_id)
        return bool(val)

    async def create_filed(self, user_id: str):
        await self.redis.rpush(user_id, "__init__")


# 单例，全局共享连接池
redis_memory = RedisMemory()

if __name__ == '__main__':
    data = asyncio.run(redis_memory.create_filed("123"))
    print(data)
