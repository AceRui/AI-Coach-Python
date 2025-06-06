import asyncio

from app.agent import agent_chat
from app.agent.agent_memory import MemoryManager

user_id = "a1233333333"
memory_manager = MemoryManager(user_id=user_id)


async def main():
    query = "修改为5-10分钟"
    langauge = "zh"
    data = await memory_manager.get_chat_history()
    for i in  data:
        print(i)

if __name__ == '__main__':
    asyncio.run(main())
