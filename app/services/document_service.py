# app/services/document_service.py
import os
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from app.models.document import Document
from app.core.retriever import HybridRetriever, get_retriever
from app.schemas.document import DocumentUploadResponse


# ========== 数据库操作函数 ==========

async def create_document_record(
    db: AsyncSession,
    user_id: int,
    filename: str,
    file_type: str,
    status: str = "processing"
) -> Document:
    """创建文档记录"""
    doc = Document(
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        status=status
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def update_document_status(
    db: AsyncSession,
    doc_id: int,
    status: str,
    chunk_count: int = 0
) -> None:
    """更新文档状态"""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if doc:
        doc.status = status
        doc.chunk_count = chunk_count
        await db.commit()


async def get_user_documents(
    db: AsyncSession,
    user_id: int
) -> list[Document]:
    """获取用户的所有文档"""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


# ========== 文档处理函数 ==========

def extract_text_from_file(file_path: str, file_type: str) -> str:
    """从文件中提取文本"""
    if file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_type == "pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        return "\n".join([doc.page_content for doc in docs])
    elif file_type == "md":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return ""


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """将文本切分为块"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )
    chunks = splitter.split_text(text)
    return chunks


def index_document(
    doc_id: int,
    user_id: int,
    filename: str,
    file_path: str,
    file_type: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> int:
    """处理文档：提取 -> 切片 -> 向量化 -> 存储"""
    # 1. 提取文本
    text = extract_text_from_file(file_path, file_type)
    if not text:
        return 0

    # 2. 切片
    chunks = split_text(text, chunk_size, chunk_overlap)
    if not chunks:
        return 0

    # 3. 构建元数据
    metadatas = [
        {
            "doc_id": doc_id,
            "user_id": user_id,
            "filename": filename,
            "chunk_index": i,
            "source": file_path
        }
        for i in range(len(chunks))
    ]

    # 4. 添加到检索器
    retriever = get_retriever()
    retriever.add_documents(chunks, metadatas)

    return len(chunks)