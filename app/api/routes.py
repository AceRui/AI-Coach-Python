from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse

from app.agent.agent_chat import multi_agent_chat
from app.agent.agent_memory import MemoryManager
from app.api.schema import ChatRequest
from app.logger import get_logger

logger = get_logger("agent_routes")

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest) -> JSONResponse:
    user_id = request.user_id
    query = request.query
    user_langauge = request.user_language
    logger.info(f"收到非流式聊天请求: user_id={user_id}, query='{query}")
    memory_manager = MemoryManager(user_id=user_id)
    try:
        response = await multi_agent_chat(user_id=user_id, query=query, memory_manager=memory_manager,
                                          user_language=user_langauge)
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"聊天处理失败: user_id={request.user_id}, error={str(e)}")
        # logger.exception("详细错误信息:")
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")
