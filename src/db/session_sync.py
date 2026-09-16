# from re import DEBUG

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings
from src.db.base import Base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.db.models import User, Session, Message, Document, Chunk

db_url = settings.DATABASE_URL
DEBUG = settings.DEBUG

# 引擎
engine = create_engine(
    url=db_url,
    echo=DEBUG, #开启SQLAlchemy的日志输出 =>SQL 会打印到控制台
)


# 会话工厂（用于创建数据库会话）
SessionLocal = sessionmaker(engine)
# async_session_factory = async_sessionmaker(
#     engine,
#     class_=AsyncSession,
#     expire_on_commit=False)
# session 依赖函数
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    """初始化数据库：创建所有表"""
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        # 所有继承Base的模型=>通过engine =>生成表
        # conn.run_sync(Base.metadata.create_all)
        print("初始化数据库成功")

def close_db():
    """关闭数据库连接"""
    engine.dispose()
    print("关闭数据库连接成功")

