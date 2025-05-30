from typing import Optional, List

import redis.asyncio as redis
import orjson

from app.config import settings


class RedisMemory:
    def __init__(self, url=settings.REDIS_DATABASE_URL, ttl=settings.REDIS_MEMORY_TTL):
        self.redis = redis.from_url(url, encoding="utf-8", decode_responses=True)
        self.ttl = ttl
        self.memory_key = settings.SHORT_MEMORY_DB_NAME  # 总表 key

    async def get_memory(self, user_id: str) -> Optional[list]:
        val = await self.redis.hget(self.memory_key, user_id)
        return orjson.loads(val) if val else []

    async def save_memory(self, user_id: str, memory: List):
        # 保存用户记忆到总表中，字段名是 user_id
        await self.redis.hset(self.memory_key, user_id, orjson.dumps(memory))
        # 设置整个 hash 的过期时间（注意：单个 field 不能设置独立过期时间）
        await self.redis.expire(self.memory_key, self.ttl)

    async def clean_memory(self, user_id: str):
        await self.redis.hdel(self.memory_key, user_id)

    async def clean_all_memory(self):
        # 删除整个 short_memory 表（慎用）
        await self.redis.delete(self.memory_key)

    async def get_all_memory(self) -> dict:
        """
        获取 memory_key 对应的所有用户记忆数据。
        返回格式: {user_id: memory_list, ...}
        """
        data = await self.redis.hgetall(self.memory_key)
        return {k: orjson.loads(v) for k, v in data.items()}


# 单例，全局共享连接池
redis_memory = RedisMemory()
