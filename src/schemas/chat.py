"""
问答相关 Pydantic 模型
"""

from datetime import datetime

from pydantic import BaseModel


class SourceItem(BaseModel):
    """来源引用项"""
    content: str
    chapter: str = ""
    section: str = ""
    score: float = 0.0


class ChatRequest(BaseModel):
    """问答请求"""
    session_id: str
    question: str


class ChatResponse(BaseModel):
    """问答响应"""
    answer: str
    sources: list[SourceItem] = []


class SessionItem(BaseModel):
    """会话列表项"""
    id: str
    title: str
    created_at: datetime


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: list[SessionItem]


class MessageItem(BaseModel):
    """消息项"""
    role: str
    content: str
    sources: list[SourceItem] | None = None
    created_at: datetime


class SessionDetailResponse(BaseModel):
    """会话详情响应"""
    messages: list[MessageItem]