
from pyexpat import model

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status

from src.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_session
from src.deps import get_current_user,get_admin_user
from src.services.document import upload_document,list_documents
from src.schemas.document import DocumentUploadResponse,DocumentListResponse,DocumentItem
from src.services.document import delete_document

router=APIRouter(
    tags=['document']
)

@router.post('/upload',response_model=DocumentUploadResponse)
async def upload(
    file:UploadFile=File(...),
    db:AsyncSession=Depends(get_session),
    user:str=Depends(get_current_user)
):
    assert file.filename is not None
    if not file.filename.endswith(('md','txt')):
        raise HTTPException(
            status_code=400,
            detail='Only .md and .txt files are supported'
        )
    filesize=file.size
    assert filesize is not None
    if filesize > 1024 * 1024 * 10 :  # 10M
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    content=await file.read()

    try:
        doc=await upload_document(
            filename=file.filename,
            content=content,
            user_id=str(user.id),
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"pload document error:{str(e)}")
    return DocumentUploadResponse(
        id=str(doc.id),
        name=doc.filename,
        status=doc.status,
        chunk_count=doc.chunk_count,
    )


@router.get("/", response_model=DocumentListResponse)
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)):
     
     docs = await list_documents(
         db
     )

     documents = []
     for doc in docs:
         documents.append(
             DocumentItem(
                 id=str(doc.id),
                 name=doc.filename,
                 status=doc.status,
                 chunk_count=doc.chunk_count,
                 file_size=doc.file_size,
                 created_at=doc.created_at,
             )
         )

     return DocumentListResponse(
        documents=documents
     )

@router.delete('/{document_id}')
async def del_document(
    document_id:str,
    current_user:User=Depends(get_admin_user),
    db:AsyncSession=Depends(get_session)
):
    
    await delete_document(document_id,db)
    return {"message": "delete success"}



# {
#   "documents": [
#     {
#       "id": "3ce6692b-3470-45ae-9de9-16404c703a99",
#       "name": "simple_university_doc.md",
#       "status": "ready",
#       "chunk_count": 36,
#       "file_size": 5456,
#       "created_at": "2026-08-19T15:27:34.977520"
#     },
#     {
#       "id": "28401060-2b17-4e92-8172-e28472f497f5",
#       "name": "simple_university_doc.md",
#       "status": "error",
#       "chunk_count": 0,
#       "file_size": 5456,
#       "created_at": "2026-08-19T15:26:00.829325"
#     },
#     {
#       "id": "f1a0c1f8-d0d5-4fab-ade6-1fe80e747977",
#       "name": "simple_university_doc.md",
#       "status": "indexing",
#       "chunk_count": 0,
#       "file_size": 5456,
#       "created_at": "2026-08-19T15:19:51.375751"
#     },
#     {
#       "id": "60e970de-a519-4cee-b227-fe74a011bed9",
#       "name": "simple_university_doc.md",
#       "status": "error",
#       "chunk_count": 0,
#       "file_size": 5456,
#       "created_at": "2026-08-19T15:15:47.297391"
#     }
#   ]
# }
