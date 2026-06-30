# app/services/background.py
import os
import threading
from app.services.vector_service import load_and_split_document, vectorize_and_store
from app.models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession


def process_document_sync(file_path: str, file_type: str, user_id: int, doc_id: int):
    """同步处理文档（用于后台线程）"""
    try:
        chunks = load_and_split_document(file_path, file_type)
        count = vectorize_and_store(
            user_id=user_id,
            doc_id=doc_id,
            chunks=chunks,
            metadata={"filename": os.path.basename(file_path)}
        )
        return {"status": "success", "chunk_count": count}
    except Exception as e:
        return {"status": "failed", "error": str(e)}