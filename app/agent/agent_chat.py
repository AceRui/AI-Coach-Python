import json
from typing import Dict, Any, List

from llama_index.core.workflow import Context
from llama_index.core.llms import ChatMessage
from llama_index.core.agent.workflow import AgentWorkflow, AgentOutput, AgentStream, ToolCall, ToolCallResult

from app.logger import get_logger
from app.agent.agent_memory import MemoryManager
from app.agent.agent_init import AgentInit

logger = get_logger("agent_chat")


async def multi_agent_chat_stream(user_id: str, query: str, memory_manager: MemoryManager, user_language: str) -> Dict[
    str, Any]:
    logger.info(f"开始对话 user_id={user_id}, query={query}, user_language={user_language}")
    logger.info(f"加载用户 {user_id} 的memory")

    # 加载用户的记忆(短期)
    memory_list = await memory_manager.load_memory()
    memory = memory_manager.format_user_memory_to_cmb(memory_list)

    # 根据用户语言，初始化Agent
    client = AgentInit(user_langauge=user_language)
    agent_workflow = client.create_multi_agent_system()

    # 创建带有Redis记忆的上下文
    ctx = Context(agent_workflow)
    await ctx.set("user_input", query)

    # 初始化状态 - 先设置再获取
    await ctx.set("state", {
        "workout_plan_params": {},
        "basic_info_params": {}
    })

    # 使用verbose=True确保详细日志
    handler = agent_workflow.run(
        user_msg=query,
        ctx=ctx,
        memory=memory,
        verbose=False
    )
    current_agent = None

    async for event in handler.stream_events():
        # 处理智能体切换事件
        if hasattr(event, "current_agent_name") and event.current_agent_name != current_agent:
            previous_agent = current_agent
            current_agent = event.current_agent_name
            logger.info(f"智能体切换: {previous_agent} -> {current_agent}")
            print(f"\n{'=' * 20} Agent: {current_agent} {'=' * 20}\n")

        # 处理智能体输出
        elif isinstance(event, AgentOutput):
            if event.response and event.response.content:
                content = event.response.content

                # 检测handoff请求
                if "目标智能体：" in content and current_agent == "路由智能体":
                    target_agent = None
                    for line in content.split("\n"):
                        if "目标智能体：" in line:
                            target_agent = line.split("：")[1].strip()
                            break

                    if target_agent:
                        logger.info(f"检测到handoff请求到: {target_agent}")
                logger.info(f"Content: {content}")

                role = event.response.role
                if role == "assistant":
                    yield f"data: {json.dumps({'type': 'text', 'content': content, 'agent': current_agent})}\n\n"

    # 在处理完所有事件后，才发送done信号
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

    short_memory_list = memory_manager.format_cmb_to_user_memory(memory)
    await memory_manager.save_short_memory(short_memory_list)
    logger.info(f"已更新用户 {user_id} 的对话记忆")


async def multi_agent_chat(user_id: str, query: str, memory_manager: MemoryManager, user_language: str) -> Dict[
    str, Any]:
    """
    非流式聊天函数，返回完整的聊天响应
    """
    logger.info(f"开始非流式对话 user_id={user_id}, query={query}, user_language={user_language}")
    logger.info(f"加载用户 {user_id} 的memory")

    # 加载用户的记忆(短期)
    memory_list = await memory_manager.load_memory()
    memory = memory_manager.format_user_memory_to_cmb(memory_list)

    # 根据用户语言，初始化Agent
    client = AgentInit(user_langauge=user_language)
    agent_workflow = client.create_multi_agent_system()

    # 创建带有Redis记忆的上下文
    ctx = Context(agent_workflow)
    await ctx.set("user_input", query)

    # 初始化状态 - 先设置再获取
    await ctx.set("state", {
        "workout_plan_params": {},
        "basic_info_params": {}
    })

    # 使用verbose=True确保详细日志
    handler = agent_workflow.run(
        user_msg=query,
        ctx=ctx,
        memory=memory,
        verbose=False
    )

    current_agent = None
    last_assistant_response = ""

    async for event in handler.stream_events():
        # 处理智能体切换事件
        if hasattr(event, "current_agent_name") and event.current_agent_name != current_agent:
            previous_agent = current_agent
            current_agent = event.current_agent_name
            logger.info(f"智能体切换: {previous_agent} -> {current_agent}")

        # 处理智能体输出
        elif isinstance(event, AgentOutput):
            if event.response and event.response.content:
                content = event.response.content

                # 检测handoff请求
                if "目标智能体：" in content and current_agent == "路由智能体":
                    target_agent = None
                    for line in content.split("\n"):
                        if "目标智能体：" in line:
                            target_agent = line.split("：")[1].strip()
                            break

                    if target_agent:
                        logger.info(f"检测到handoff请求到: {target_agent}")

                logger.info(f"Content: {content}")

                role = event.response.role
                if role == "assistant":
                    # 只保留最后一个assistant角色的输出
                    last_assistant_response = content

    # 保存对话记忆
    short_memory_list = memory_manager.format_cmb_to_user_memory(memory)
    await memory_manager.save_short_memory(short_memory_list)
    logger.info(f"已更新用户 {user_id} 的对话记忆")
    
    # 返回最后一个assistant角色的输出
    return {
        "response": last_assistant_response,
        "agent": current_agent
    }
