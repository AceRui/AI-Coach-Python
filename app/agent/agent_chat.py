from typing import Dict, Any

from llama_index.core.workflow import Context
from llama_index.core.agent.workflow import AgentOutput, ToolCall, ToolCallResult
from llama_index.core.llms import ChatMessage, MessageRole

from app.logger import get_logger
from app.agent.agent_memory import MemoryManager
from app.agent.agent_init import AgentInit

logger = get_logger("agent_chat")


async def multi_agent_chat(
        user_id: str, query: str, memory_manager: MemoryManager, user_language: str
) -> Dict[str, Any]:
    """
    非流式聊天函数，返回完整的聊天响应
    """
    logger.info(
        f"开始非流式对话 user_id={user_id}, query={query}, user_language={user_language}"
    )

    # 初始化Memory并加载历史对话
    memory = await memory_manager.init_memory()
    logger.info(f"初始化Memory完成，用户ID: {user_id}")

    # 根据用户语言，初始化Agent
    client = AgentInit(user_language=user_language)
    agent_workflow = client.create_multi_agent_system()

    # 初始化Context
    ctx = Context(agent_workflow)
    await ctx.set("user_id", user_id)
    await ctx.set("memory", memory)

    # 运行Agent工作流 - 非流式处理
    response_content = ""
    current_agent = ""
    try:
        # 添加助手响应到Memory
        handler = agent_workflow.run(user_msg=ChatMessage(content=query), ctx=ctx, verbose=True, memory=memory)
        async for event in handler.stream_events():
            if isinstance(event, AgentOutput):
                logger.debug(f"AgentOutput: {event.current_agent_name}")
                logger.debug(f"AgentOutput: {event.response.content}")
                if event.response.role == "assistant":
                    response_content = event.response.content
                    current_agent = event.current_agent_name

            if isinstance(event, ToolCall):
                logger.debug(f"ToolCall: {event.tool_name}")
                logger.debug(f"ToolCall: {event.tool_kwargs}")
            if isinstance(event, ToolCallResult):
                logger.debug(f"ToolCallResult: {event.tool_name}")
                logger.debug(f"ToolCallResult: {event.tool_output}")

        await memory_manager.save_memory_to_redis(memory)

        logger.info(f"Response content: {response_content}")
        return {
            "response": response_content,
            "agent": current_agent,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Agent执行出错: {str(e)}")

        # 即使出错也要保存Memory
        try:
            await memory_manager.save_memory_to_redis(memory)
        except Exception as save_error:
            logger.error(f"保存Memory失败: {str(save_error)}")

        return {
            "response": f"抱歉，处理您的请求时出现了错误: {str(e)}",
            "agent": "error_handler",
            "status": "error"
        }
