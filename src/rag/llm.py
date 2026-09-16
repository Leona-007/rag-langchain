from langchain_core.language_models import BaseLanguageModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from src.config import settings
from pydantic import SecretStr


def get_llm() -> BaseLanguageModel:

    provider = settings.LLM_PROVIDER

    if provider == "deepseek":
        return ChatDeepSeek(
            model=settings.DEEPSEEK_MODEL,
            api_key=SecretStr(settings.DEEPSEEK_API_KEY)  ,
            base_url=settings.DEEPSEEK_BASE_URL
        ) 
    elif provider == "openai":
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=SecretStr(settings.OPENAI_API_KEY),
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.5,
            max_retries=3,
        )

    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )

    
