from typing import Dict, List

from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage

from app.logger import get_logger

from app.db.redis.session import redis_memory

logger = get_logger("memory_manager")


class MemoryManager:
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def load_short_memory(self) -> List:
        short_memory = await redis_memory.get_memory(self.user_id)
        return short_memory

    async def save_short_memory(self, memory: List):
        await redis_memory.save_memory(self.user_id, memory)

    async def clean_short_memory(self):
        await redis_memory.clean_memory(self.user_id)

    @staticmethod
    def format_user_memory_to_cmb(memory_list: List) -> ChatMemoryBuffer:
        memory = ChatMemoryBuffer.from_defaults(token_limit=40000)
        if not memory_list:
            return memory

        chat_history = []
        for index_memory in memory_list:
            chat_history.append(
                ChatMessage(
                    role=index_memory["role"],
                    content=index_memory["content"]
                )
            )
        memory.put_messages(chat_history)
        return memory

    @staticmethod
    def format_cmb_to_user_memory(cmb_memory: ChatMemoryBuffer) -> List[Dict]:
        chat_history = []
        for message in cmb_memory.get_all():
            role = message.role.value
            blocks = message.blocks
            if not blocks:
                break
            content = blocks[0].text
            chat_history.append({"role": role, "content": content})
        return chat_history

    async def load_memory(self):
        short_memory = await self.load_short_memory()
        if short_memory:
            logger.debug(f"加载短期记忆, {short_memory}")
            return short_memory
        return []
    # def trigger_persist_memory(self):
    #     """触发异步持久化任务，将短期记忆保存到长期存储"""
    #     # 导入在函数内部，避免循环导入
    #     from app.tasks.memory_tasks import persist_user_memory
    #
    #     # 使用delay方法异步调用Celery任务
    #     persist_user_memory.delay(self.user_id)
    #     logger.info(f"已触发用户 {self.user_id} 的记忆持久化任务")
