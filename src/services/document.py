import os
import uuid
from sqlalchemy import select
from torch import chunk
from src.db.models import Chunk, Document
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from src.config import settings
from src.rag.store import store_document,delete_document_points


# 文档列表
async def list_documents(db:AsyncSession) -> list[Document]:
    result = await db.execute(
          select(Document).order_by(Document.created_at.desc()) # 按创建时间降序排序,desc() 表示降序排序
        )
    return  list(result.scalars().all())

# 文档上传
async def upload_document(
    filename: str, 
    content: bytes,
    user_id: str,
    db: AsyncSession,
) -> Document:

    """
    文档上传：
    1. 保存文档到本地磁盘
    2. 保存文档元数据到postgresql数据库（documents表)）
    3. 文档分割为多个chunks
    4. 保存chunks到qdrant数据库
    5. chunks元数据 保存到postgresql 数据库 (chunks表)
    6. 更新文档状态为 ready 和 chunk_count (documents表)

    异常处理：
           更新文档状态为 error 
    
    返回：
          文档对象 (前提是文档上传成功 : 磁盘 + postgresql + qdrant)
    
    """

    #   保存文件到本地磁盘
    data_dir = Path(settings.DATA_DIR)
    data_dir.mkdir(exist_ok=True) # exist_ok 如果路径已经存在，不抛出异常

    new_filename = f"{uuid.uuid4()}_{filename}"
    file_path = data_dir / new_filename
    file_path.write_bytes(content) # 写入文件, write_bytes : 写入二进制数据

    #   保存文档元数据到postgresql数据库
    document = Document(
        user_id=user_id,
        filename=filename, # abc.md
        title= Path(filename).stem, # abc
        file_path=str(file_path),
        file_size=len(content),
        status="indexing"
    )

    db.add(document)
    await db.commit() # 同步到数据库
    await db.refresh(document) # 刷新对象

    try:
        
        #  文档分割为多个chunks + 保存chunks到qdrant数据库
        # chunks = split(load(file_path))
        # print('chunks:-----', len(chunks))
        result = store_document(str(file_path))

        # chunks元数据 保存到postgresql 数据库 (chunks表)
        chunk_count = result.get("chunk_count")
        qdrant_ids = result.get("qdrant_ids")
        chunks = result.get("chunks")

        for chunk,qdrant_id in zip(chunks,qdrant_ids):
            chunk_pg = Chunk(
                document_id=document.id,
                content=chunk.page_content,
                extra_meta=chunk.metadata,
                qdrant_id=qdrant_id,
            )
            db.add(chunk_pg)
        await db.commit() 


        #  更新文档状态为 ready 和 chunk_count (documents表)
        document.status = "ready"
        document.chunk_count = chunk_count
        await db.commit()
       
    except Exception as e:
        
        document.status = "error"
        await db.commit() # 同步到数据库
        raise e
     

    return document

# 删除文档
async def delete_document(doc_id: str, db: AsyncSession):
    """
    删除文档
    1,从qdrant数据库删除文档
    2,从本地磁盘删除文档
    3,从postgresql数据库删除文档
     
    """
    result=await db.execute(
        select(Document).where(Document.id==doc_id)
    )
    doc=result.scalar_one_or_none()
    if not doc:
        return
    chunk_result=await db.execute(
        select(Chunk.qdrant_id).where(Chunk.document_id==doc_id)
    )
    qdrant_ids =chunk_result.scalars().all()
    if qdrant_ids:
        delete_document_points(qdrant_ids) # type: ignore

    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    await db.delete(doc)
    await db.commit()

