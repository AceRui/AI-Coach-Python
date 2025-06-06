from llama_index.llms.google_genai import GoogleGenAI

from app.config import settings


def gemini_llm() -> GoogleGenAI:
    llm = GoogleGenAI(api_key=settings.GOOGLE_API_KEY, model=settings.GOOGLE_MODEL)
    return llm
