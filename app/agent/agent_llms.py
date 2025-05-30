from llama_index.llms.google_genai import GoogleGenAI
from llama_index.llms.ollama import Ollama

from app.config import settings


def gemini_llm() -> GoogleGenAI:
    llm = GoogleGenAI(
        api_key=settings.GOOGLE_API_KEY,
        model=settings.GOOGLE_MODEL
    )
    return llm


def ollama_llm() -> Ollama:
    llm = Ollama(
        model=settings.OLLAMA_MODEL,
        request_timeout=120
    )
    return llm
