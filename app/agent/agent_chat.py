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

    # 添加用户消息到Memory，避免重复添加
    user_message = ChatMessage(role=MessageRole.USER, content=query)
    # memory.put(user_message)
    logger.debug(f"添加用户消息到Memory: {query}")

    # 根据用户语言，初始化Agent
    client = AgentInit(user_language=user_language)
    agent_workflow = client.create_multi_agent_system()

    # 初始化Context
    ctx = Context(agent_workflow)
    await ctx.set("user_id", user_id)
    await ctx.set("memory", memory)
    logger.debug(f"Start Memory: {memory.get_all()}")
    # 运行Agent工作流 - 非流式处理
    response_content = ""
    current_agent = ""
    try:
        # 直接运行并等待完成，不使用流式处理
        # result = await agent_workflow.run(
        #     user_msg=user_message,
        #     ctx=ctx,
        #     memory=memory,
        #     verbose=True
        # )
        #
        # # 提取响应内容
        # current_agent = "unknown"
        #
        # # 处理AgentOutput类型的结果
        # if isinstance(result, AgentOutput):
        #     # 检查是否有工具调用
        #     if result.tool_calls and len(result.tool_calls) > 0:
        #         # 实际执行工具调用
        #         for tool_call in result.tool_calls:
        #             logger.info(f"执行工具调用: {tool_call.name}, 参数: {tool_call.args}")
        #             try:
        #                 # 查找对应的工具并执行
        #                 tool_result = await agent_workflow.step(
        #                     tool_call=tool_call,
        #                     ctx=ctx,
        #                     memory=memory
        #                 )
        #                 logger.info(f"工具调用结果: {tool_result}")
        #             except Exception as tool_error:
        #                 logger.error(f"工具调用失败: {str(tool_error)}")
        #
        #     # 提取响应内容，去除可能的role前缀
        #     response_content = str(result.response)
        #     # 检查并移除可能的role前缀，如"Assistant: "或"AI: "
        #     role_prefixes = ["Assistant: ", "AI: ", "Sarah: "]
        #     for prefix in role_prefixes:
        #         if response_content.startswith(prefix):
        #             response_content = response_content[len(prefix):].strip()
        #             break
        # elif hasattr(result, 'content'):
        #     response_content = str(result.content)
        #     # 检查并移除可能的role前缀
        #     role_prefixes = ["Assistant: ", "AI: ", "Sarah: "]
        #     for prefix in role_prefixes:
        #         if response_content.startswith(prefix):
        #             response_content = response_content[len(prefix):].strip()
        #             break
        # else:
        #     response_content = str(result)
        #     # 检查并移除可能的role前缀
        #     role_prefixes = ["Assistant: ", "AI: ", "Sarah: "]
        #     for prefix in role_prefixes:
        #         if response_content.startswith(prefix):
        #             response_content = response_content[len(prefix):].strip()
        #             break

        # 添加助手响应到Memory
        handler = agent_workflow.run(user_msg=ChatMessage(content=query), ctx=ctx, verbose=True, memory=memory)
        async for event in handler.stream_events():
            if isinstance(event, AgentOutput):
                logger.debug(f"Event: {event.response}")
                if event.response.role == "assistant":
                    response_content = event.response.content
                    current_agent = event.current_agent_name

            if isinstance(event, ToolCall):
                logger.debug(f"Event: {event.tool_name}")
                logger.debug(f"Event: {event.tool_kwargs}")
            if isinstance(event, ToolCallResult):
                logger.debug(f"Event: {event.tool_name}")
                logger.debug(f"Event: {event.tool_output}")
            logger.debug("*" * 100)

        logger.debug(f"End Memory: {memory.get_all()}")
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
