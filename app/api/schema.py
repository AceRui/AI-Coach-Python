from pydantic import BaseModel


class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_id: str
    query: str
    user_language: str
