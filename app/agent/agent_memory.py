import asyncio
from typing import Dict, List

from llama_index.core.memory import Memory
from llama_index.core.llms import ChatMessage
from llama_index.storage.chat_store.redis import RedisChatStore

from app.logger import get_logger
from app.config import settings

logger = get_logger("memory_manager")


class MemoryManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.chat_store = RedisChatStore(
            ttl=settings.REDIS_MEMORY_TTL,
            redis_url=settings.REDIS_DATABASE_URL,
        )

    async def init_memory(self) -> Memory:
        """初始化Memory实例并从Redis加载历史对话"""
        # 创建Memory实例
        memory = Memory.from_defaults(
            token_limit=40000,
            session_id=self.user_id,
        )

        # 从Redis加载历史对话
        chat_history = await self.chat_store.aget_messages(self.user_id)
        if chat_history:
            # 将历史消息添加到Memory中
            memory.put_messages(chat_history)
            logger.info(f"从Redis加载了 {len(chat_history)} 条历史消息")

        return memory

    async def save_memory_to_redis(self, memory: Memory):
        """将Memory中的消息保存到Redis，避免重复保存"""
        # 获取当前Memory中的所有消息
        current_messages = await memory.aget_all()
        if not current_messages:
            logger.info("Memory中没有消息，无需保存")
            return
        self.chat_store.set_messages(key=self.user_id, messages=current_messages)

    async def get_chat_history(self) -> List[ChatMessage]:
        """直接从Redis获取聊天历史"""
        return await self.chat_store.aget_messages(self.user_id)
