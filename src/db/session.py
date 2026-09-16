from re import DEBUG

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings
from src.db.models import Base #注意 先导入模型 才能使用Base创建表
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

db_url = settings.DATABASE_URL
# DEBUGs = settings.DEBUG

# 引擎
engine = create_async_engine(
    url=db_url,
    echo=settings.DEBUG, #开启SQLAlchemy的日志输出 =>SQL 会打印到控制台
)


# 会话工厂（用于创建数据库会话）
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False)

# session 依赖函数
async def get_session():
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            print(e)
            raise e
        finally:
            await session.close()

async def init_db():
    """初始化数据库：创建所有表"""
    async with engine.begin() as conn:
        # 所有继承Base的模型=>通过engine =>生成表
        # Base.metadata.create_all(bind=engine)
        await conn.run_sync(Base.metadata.create_all)
        print("初始化数据库成功")

async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    print("关闭数据库连接成功")

