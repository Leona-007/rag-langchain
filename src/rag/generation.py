from unittest import result

from src.rag.store import get_vector_store
from src.rag.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from src.rag.retriver import retriver
import asyncio

SYSTEM_PROMPT = """你是一个校园生活助手，请严格遵循以下规则：

1. 仅基于提供的上下文内容回答问题
2. 如果上下文不足以回答，如实说明"文档中没有相关信息"，不要编造
3. 使用中文回答，语言简洁易懂
4. 涉及数字、时间、地点等信息时，引用原文

上下文：
{context}"""

async def ask_question(query: str,history:list | None = None) -> dict:
    vector_store = get_vector_store()
    llm=get_llm()
    docs_str, sources = retriver(query)
    
    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(
                    variable_name="chat_history", optional=True
                ),  # 聊天历史 可选
                ("human", "{input}"),
            ]
        )
    
        #  定义链 ： dict ->prompt -> llm ->解析 -> anwser
        # StrOutputParser 得使用实例
    chain = prompt | llm | StrOutputParser()
    answer =await chain.ainvoke(
        {"context": docs_str, "input": query, "chat_history": history or []}
    )
    
    print(f"生成的答案:", answer)
    print(f"答案来源:", sources)
    
    return {"answer": answer, "sources": sources}
    

async def stream_event_generator(question:str,session_id:str):
        from src.services.chat import _save_message_ai
        # 检索
        docs_str, sources = retriver(query=question)

        #  获取大模型

        llm = get_llm()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "{input}"),
            ]
        )

        chain = prompt | llm

        # 返回值：AsyncIterator
        answer_parts = []
        # llm 每次生成一个token也叫chunk
        async for chunk in chain.astream(
            {"context": docs_str, "input": question}
        ):

            content = chunk.content if hasattr(chunk, "content") else str(chunk)
            if content:
                # 追加到answer_parts列表
                answer_parts.append(content)

                # 通过SSE 推送给前端
                yield {"data": {"type": "token", "content": content}}

        # 返回检索来源
        yield {"data": {"type": "source", "sources": sources}}

        # 标记流结束
        yield {"data": {"type": "done"}}
        asyncio.ensure_future(
            _save_message_ai(session_id=session_id, question= question,answer=str(answer_parts), sources=sources)
        )    


if __name__ == "__main__":
    
    query = "宿舍几点关门?"
    asyncio.run(ask_question(query=query))
    
    
    # print(result)