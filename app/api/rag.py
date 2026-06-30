# app/api/rag.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.retriever import HybridRetriever
from app.dependencies import get_current_active_user
from app.models.user import User
from langchain_openai import ChatOpenAI
from app.config import settings

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])

# 初始化检索器和 LLM
retriever = HybridRetriever()

llm = ChatOpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=settings.ZHIPU_API_KEY,
    model="glm-4-flash",
    temperature=0.5
)


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class SourceInfo(BaseModel):
    chunk: str
    source: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]


@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """基于知识库问答"""
    # 1. 检索相关文档块
    results = retriever.hybrid_search(
        query=request.query,
        top_k=request.top_k,
        alpha=0.5
    )

    if not results:
        return QueryResponse(
            answer="未找到相关信息，请先上传文档。",
            sources=[]
        )

    # 2. 构建上下文
    context = "\n\n".join([f"[来源 {i+1}]\n{r['chunk']}" for i, r in enumerate(results)])

    # 3. 生成回答
    prompt = f"""请根据以下参考资料回答用户的问题。

参考资料：
{context}

用户问题：{request.query}

请基于参考资料回答，如果参考资料中没有相关信息，请明确说明。
"""
    response = llm.invoke(prompt)

    return QueryResponse(
        answer=response.content,
        sources=[
            SourceInfo(
                chunk=r["chunk"],
                source=r["metadata"].get("filename", "未知"),
                score=r["score"]
            )
            for r in results
        ]
    )