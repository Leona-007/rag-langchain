from pathlib import Path

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from src.config import settings
from qdrant_client.models import Payload, PointStruct, VectorParams, Distance
from src.rag.embedding import get_embedding
from src.rag.loader import load
from src.rag.splitter import split

def get_qdrant_client()->QdrantClient:
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )
def get_vector_store()->QdrantVectorStore:
    client=get_qdrant_client()
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=settings.QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE

            )
        )
    embedding=get_embedding()
    return QdrantVectorStore(
        client=client,
        collection_name=settings.QDRANT_COLLECTION,
        embedding=embedding
    )    
def store_document(file_path: str) -> dict:
    # 加载存储文档
     doc_str = load(file_path)
    #  分割文档
     chunks = split(doc_str)
    #  存储文档
     vector_store = get_vector_store()
     ids = vector_store.add_documents(chunks)

    # 支持异步批量写入
    #  texts = [chunk.content for chunk in chunks]
    #   metadatas = [chunk.extra_meta for chunk in chunks]
    #  ids = vector_store.aadd_texts(texts,metadatas) # 异步批量存储


     return {"qdrant_ids":ids,"chunk_count":len(chunks),"chunks":chunks}

def delete_document_points(qdrant_ids: list[str]):
    client=get_qdrant_client()
    client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=qdrant_ids
    )

if __name__ == "__main__":
    from src.rag.loader import load
    from src.rag.splitter import split
    

    file_path = Path(__file__).resolve().parent.parent.parent/"data"/"simple_university_doc.md"

    doc_str = load(file_path) # type: ignore
    # print(doc_str)

    chunks = split(doc_str)
    # print(chunks)

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    

    # cd src
    # uv run python -m src.rag.store