"""
文档管理相关 Pydantic 模型
"""

from datetime import datetime
from pydantic import BaseModel

class DocumentItem(BaseModel):
    """文档列表项"""
    id: str
    name: str
    status: str  # pending | indexing | ready | error
    chunk_count: int = 0
    file_size: int = 0
    created_at: datetime


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    documents: list[DocumentItem]


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    id: str
    name: str
    status: str
    chunk_count: int = 0


class DocumentReindexResponse(BaseModel):
    """文档重索引响应"""
    message: str
    chunk_count: int