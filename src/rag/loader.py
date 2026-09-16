from langchain_community.document_loaders import TextLoader

def load(file_path:str)->str:
    loader=TextLoader(file_path=file_path,encoding='utf-8')
    documents=loader.load()
    return documents[0].page_content