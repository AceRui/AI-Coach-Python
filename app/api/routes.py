from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.agent.agent_chat import multi_agent_chat_stream
from app.agent.agent_memory import MemoryManager
from app.api.schema import ChatRequest
from app.logger import get_logger

logger = get_logger("agent_routes")

router = APIRouter()


@router.post("/stream-chat")
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    user_id = request.user_id
    query = request.query
    user_langauge = request.user_language
    logger.info(f"收到聊天请求: user_id={user_id}, query='{query}")
    memory_manager = MemoryManager(user_id=user_id)
    try:
        async def get_chat():
            async for chunk in multi_agent_chat_stream(user_id=user_id, query=query, memory_manager=memory_manager,
                                                       user_language=user_langauge):
                yield chunk

        return StreamingResponse(
            get_chat(),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"聊天处理失败: user_id={request.user_id}, error={str(e)}")
        # logger.exception("详细错误信息:")
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")
