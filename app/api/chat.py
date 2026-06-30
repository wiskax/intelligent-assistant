# app/api/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.core.retriever import get_retriever
from langchain_openai import ChatOpenAI
from app.config import settings

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


class Source(BaseModel):
    content: str
    filename: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []


llm = ChatOpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=settings.ZHIPU_API_KEY,
    model="glm-4-flash",
    temperature=0.3
)


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """基于用户文档库回答问题（使用混合检索）"""
    
    # 1. 使用混合检索
    retriever = get_retriever()
    
    # 先获取所有结果，再按用户过滤
    all_results = retriever.hybrid_search(
        query=request.query,
        top_k=request.top_k * 2,  # 多取一些，再过滤
        alpha=0.5  # 向量和 BM25 各占 50%
    )
    
    # 过滤出当前用户的文档
    user_results = [
        r for r in all_results 
        if r["metadata"].get("user_id") == current_user.id
    ][:request.top_k]
    
    if not user_results:
        return ChatResponse(
            answer="未找到相关信息，请先上传相关文档。",
            sources=[]
        )
    
    # 2. 构建上下文
    context = "\n\n".join([r["chunk"] for r in user_results])
    sources = [
        Source(
            content=r["chunk"],
            filename=r["metadata"].get("filename", "未知"),
            score=r["score"]
        )
        for r in user_results
    ]
    
    # 3. 生成回答
    prompt = f"""根据以下文档内容回答用户问题。如果信息不足，请说明。

文档内容：
{context}

用户问题：{request.query}

请基于文档内容给出准确的回答："""
    
    response = llm.invoke(prompt)
    
    return ChatResponse(
        answer=response.content,
        sources=sources
    )