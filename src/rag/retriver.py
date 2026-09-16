from src.rag.store import get_vector_store
from src.config import settings
def retriver(query):
    vector_store = get_vector_store()
    docs_with_scores=vector_store.similarity_search_with_score(query,settings.RETRIEVER_TOP_K)
    docs_text = ''
    sources = []
    for doc, score in docs_with_scores:
            docs_text += f"{doc.page_content}\n"
            source = {
                "content": doc.page_content[:30], 
                "score": round(score,4),
                "chapter": doc.metadata.get("chapter", ""),  # 所属章节
                "section": doc.metadata.get("section", ""),  # 所属小节
            }
            sources.append(source)
    
    
    return  (docs_text, sources)
    