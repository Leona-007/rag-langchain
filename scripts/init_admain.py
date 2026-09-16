
from src.db.session import get_session,async_session_factory, engine
from src.db.models import Base, User
from src.utils.password import get_password_hash, verify_password
import asyncio
from sqlalchemy import select

async def init():

    # 初始化数据库表
    async with engine.begin() as conn:
        # 所有继承Base的模型=>通过engine =>生成表
        # Base.metadata.create_all(bind=engine)
        await conn.run_sync(Base.metadata.create_all)
        print("初始化数据库成功")


    # 通过session 创建管理员
    async with async_session_factory() as session:
         # 判断邮箱是否存在
        existing_user = await session.execute(
            select(User).where(User.email == "admin@campu.com")
        )
        if not existing_user.scalar_one_or_none():
            # 创建用户对象
            admin = User(
                role = "admin", 
                email="admin@campu.com",
                password_hash = get_password_hash("123456")
                )
            session.add(admin) # 添加用户实例信息到会话
            await session.commit() # 数据库提交 数据持久化
            print("✅ 管理员已创建：admin@campus.com / 12345678")
        else:
            print("ℹ  管理员已存在，跳过")

    await engine.dispose()
    print("🎉 初始化完成！")

if __name__ == "__main__":
    asyncio.run(init())
    
        
            