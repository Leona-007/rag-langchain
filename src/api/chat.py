
from email import message
from logging import config

from fastapi import APIRouter, Depends
from src.db.models import User
from src.deps import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_session
from src.services.chat import process_question,create_session,get_user_sessions,del_user_sessions,get_session_detail
from src.schemas.chat import  SourceItem,ChatRequest,ChatResponse,MessageItem,SessionDetailResponse,SessionItem,SessionListResponse


router=APIRouter(
    tags=['chat']
)


@router.post("/sessions", status_code=201)
async def new_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):

    session = await create_session(
        user_id=str(current_user.id),
        db=db
    )

    return {"session_id": str(session.id), "title": session.title}

@router.get('/sessions',response_model=SessionListResponse)
async def list_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await get_user_sessions(
        user_id=str(current_user.id),
        db=db
    )
    session_items = []
    for session in result:
        session_item = SessionItem(
            id=str(session.id),
            title=session.title,
            created_at=session.created_at
        )
        session_items.append(session_item)

    return SessionListResponse(sessions=session_items)

@router.delete("/sessions/{session_id}")
async def remove_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await del_user_sessions(
        session_id=session_id,
        db=db
    )

    return {"message": "Session deleted"}

@router.get('/sessions/{session_id}',response_model=SessionDetailResponse)
async def get_chat_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result= await get_session_detail(session_id=session_id,db=db)
    messages = [
        MessageItem(
            role= m.role,
            content=m.content,
            sources=m.sources,
            created_at=m.created_at,
        )
        for m in result
    ]

    return SessionDetailResponse(messages=messages)

@router.post("/sessions/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    '''
        非流式
    '''
    # print(f"request---user-------{current_user}")
    # print(f"request-------{request}")

    response = await process_question(
        question=request.question, session_id=request.session_id, db=db
    )
    answer = response.get("answer")
    sources = response.get("sources", [])

    source_items = [
        SourceItem(
            chapter=s.get("chapter"),
            section=s.get("section"),
            content=s.get("content"),
            score=s.get("score"),
        )
        for s in sources
    ]

    return ChatResponse(answer=str(answer), sources=source_items)

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    流式问答 : SSE协议
    token 形式返回llm结果 实现前端打字机效果

    # token 事件：llm 文本片段
    # source事件：来源
    # done事件：完成

    """
    from src.rag.generation import stream_event_generator
    from sse_starlette.sse import EventSourceResponse  # fastapi 进行sse协议响应
    from src.services.chat import _save_message_user
    await _save_message_user(question=request.question,session_id=request.session_id,db=db)
    
    # EventSourceResponse 将生成器包装为 SSE 响应
    return EventSourceResponse(stream_event_generator(session_id=request.session_id,question=request.question))

