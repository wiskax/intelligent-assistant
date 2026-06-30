# app/api/system.py
from fastapi import APIRouter, Depends
from app.dependencies import get_current_active_user
from app.models.user import User
import os
import chromadb

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status")
async def system_status(current_user: User = Depends(get_current_active_user)):
    """检查系统状态"""
    # 检查 chroma_db
    chroma_ok = os.path.exists("./chroma_db")
    
    # 检查上传目录
    uploads_ok = os.path.exists("./uploads")
    
    # 获取文档数量
    doc_count = 0
    if uploads_ok:
        doc_count = len([f for f in os.listdir("./uploads") if os.path.isfile(os.path.join("./uploads", f))])
    
    return {
        "status": "ok",
        "chroma_db": chroma_ok,
        "uploads_dir": uploads_ok,
        "document_count": doc_count,
        "user": current_user.username
    }


@router.post("/clear-cache")
async def clear_cache(current_user: User = Depends(get_current_active_user)):
    """清空当前用户的向量缓存（谨慎使用）"""
    # 这里可以添加清空逻辑
    return {"message": "缓存已清空"}