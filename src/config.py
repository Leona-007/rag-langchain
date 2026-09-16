from pathlib import Path
from pydantic_settings import BaseSettings,SettingsConfigDict


APP_DIR = Path(__file__).resolve().parent.parent


# 继承 BaseSettings :动从环境变量文件中读取配置项
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=APP_DIR / ".env", # env配置文件路径 项目根目录下
        env_file_encoding="utf-8",
        extra="ignore", # 忽略未定义的配置项
        )

    # 定义配置项
    APP_NAME: str = "Campus RAG System" # 默认值
    DEBUG: bool = False

    # 数据库
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "Leona050502"
    DB_NAME: str = "campus_rag"

    @property
    def DATABASE_URL(self) -> str:
        # return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "campus_knowledge"
    QDRANT_VECTOR_SIZE: int = 768  # bge-base-zh 的维度

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

     # LLM 提供商
    LLM_PROVIDER: str = "deepseek"

    DEEPSEEK_API_KEY: str = "sk-cdbd98cdaf8f4eeb9073295873a55714"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    OPENAI_API_KEY:str =""
    OPENAI_BASE_URL:str = "https://api.openai.com/v1"
    OPENAI_MODEL:str = "gpt-3.5-turbo"

    OLLAMA_BASE_URL:str = "http://localhost:11434"
    OLLAMA_MODEL:str = "qwen2.5:0.5b"

    # RAG
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVER_TOP_K: int = 3
    SHOW_SOURCE:bool =True # 是否显示来源文档
    DATA_DIR: str = "data"


# 实例化配置
settings = Settings()



if __name__ == "__main__":
    print(settings.DEBUG) 
    print(settings.DATABASE_URL) 

