
from typing import List
from uuid import uuid4
from mcp_types import Role
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sympy import content
from src.db.models import Session,Message
from src.rag.generation import ask_question

# 创建新对话
async def create_session(user_id: str, db: AsyncSession) -> Session:
    session = Session(
        user_id=user_id
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
# 获取当前用户对话
async def get_user_sessions(user_id: str, db: AsyncSession) -> list[Session]:
    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(Session.created_at.desc())
    )

    return list(result.scalars().all())
# 删除对话
async def del_user_sessions(       
    session_id:str,
    db:AsyncSession
):
    result=await db.execute(
        select(Session).where(Session.id==session_id)
    )
    session=result.scalar_one_or_none()
    if session:
        await db.delete(session)
        await db.commit()

# 获取对话内容
# 获取session详情 ： 消息列表
async def get_session_detail(session_id: str, db: AsyncSession):
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
    )

    return list(result.scalars().all())

async def process_question(
    question:str,
    session_id:str,
    db:AsyncSession
):
    message=Message(
        session_id=session_id,
        content=question,
        role='user'
    )
    db.add(message)
    await db.commit()
    history=await get_session_detail(session_id,db)
    history_messages=[
        {
            "role":h.role,
            "content":h.content
        }
        for h in history[:-1]
    ]
    response=await ask_question(question,history_messages)
    answer=response['answer']
    sources = response.get("sources",[])
    # 存储AI消息到数据库
    ai_msg = Message(
        session_id=session_id,
        role="assistant",
        content=answer,
        sources=sources,
    )
    db.add(ai_msg)
    await db.commit()

    # 会话标题修改
    session_result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if session and session.title == "新对话":
        session.title = question[:10]
        await db.commit()

    return response

async def _save_message_user(question:str,
    session_id:str,
    db:AsyncSession):
    user_message=Message(
        content=question,
        session_id=session_id,
        role='user'
    )
    db.add(user_message)
    await db.commit()

async def _save_message_ai(session_id: str,  question: str, answer: str,sources:list):
    from src.db.session import async_session_factory
    async with async_session_factory() as db:
         
         assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=answer,
            sources=sources,
        )
         db.add(assistant_msg)
         await db.commit()

         # 会话标题修改
         session_result = await db.execute(
            select(Session).where(Session.id == session_id)
         )
         session = session_result.scalar_one_or_none()
         if session and session.title == "新对话":
            session.title = question[:10]
            await db.commit()

