from langchain_huggingface import HuggingFaceEmbeddings
# 缓存嵌入模型 避免重复加载
from functools import lru_cache

@lru_cache(maxsize=1)
def get_embedding()->HuggingFaceEmbeddings:
    model_name="BAAI/bge-base-zh-v1.5"
    model_kwargs={'device':'cpu'}
    encode_kwargs={'normalize_embeddings':True}
    hf=HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return hf