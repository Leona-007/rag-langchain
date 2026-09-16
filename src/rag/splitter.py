from langchain_text_splitters import MarkdownHeaderTextSplitter,RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
def split(markdown_document:str)->List[Document]:
    headers_to_split_on=[
        ("##","chapter"),
        ("###","section")
    ]
    markdown_splitter=MarkdownHeaderTextSplitter(headers_to_split_on)
    md_doc=markdown_splitter.split_text(markdown_document)

    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=30,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],  # 优先级
    )
    chunks=text_splitter.split_documents(md_doc)
    return chunks