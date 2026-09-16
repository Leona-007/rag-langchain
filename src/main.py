
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.session import init_db,close_db
from src.config import settings
from contextlib import asynccontextmanager
from src.api.auth import router as auth_router
from src.api.chat import router as chat_router
from src.api.document import router as document_router

# @asynccontextmanager
# async def lifespan(app:FastAPI):
#     '应用生命周期'
#     try:
#         init_db()
#     except Exception as e:
#         print('初始化数据库失败')
#     yield #等待
#     close_db()

# lifespan 是FastAPI生命周期的钩子
@asynccontextmanager
async def lifespan(app:FastAPI):
    """应用生命周期管理"""

    # 应用执行前初始化： 初始化数据库
    try:
        # 初始化数据库
        await init_db()
    except Exception as e:
        print(f"初始化数据库失败")
        print(e)
        raise e

    yield # 等待 fastapi 接受请求 服务器运行

    # 应用关闭后释放资源： 关闭数据库
    await close_db()

app=FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

root_router=APIRouter(prefix='/root')
app.include_router(root_router)
root_router.include_router(auth_router)
root_router.include_router(chat_router)
root_router.include_router(document_router)


origins = [
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"], # 允许所有源访问
    allow_origins=origins, # 允许所有源访问
    allow_credentials=True, # 允许携带凭证
    # allow_methods=["*"], # 允许所有请求方法  GET POST PUT DELETE OPTIONS
    allow_methods=["GET"], # 允许GET请求方法
    allow_headers=["*"], # 允许所有请求头
)
@app.get('/')
async def root():
    return 'hello'