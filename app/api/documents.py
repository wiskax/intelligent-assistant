# app/api/documents.py
import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.services import document_service
from app.services.vector_service import vectorize_and_store, load_and_split_document
from app.schemas.document import DocumentUploadResponse, DocumentListResponse
from app.core.retriever import _global_retriever, get_retriever

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """上传文档（PDF / TXT / MD），自动向量化"""
    allowed_types = ["pdf", "txt", "md"]
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(allowed_types)}"
        )

    # 保存文件
    file_id = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_id)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 创建文档记录
    doc = await document_service.create_document_record(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        file_type=file_ext,
        status="processing"
    )

    try:
        print(f"📄 开始处理文档: {file.filename}")
        
        # 1. 加载并切分文档
        chunks = load_and_split_document(file_path, file_ext)
        print(f"✅ 切分成 {len(chunks)} 个块")
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文档内容为空，无法处理"
            )
        
        # 2. 向量化并存储
        chunk_count = vectorize_and_store(
            user_id=current_user.id,
            doc_id=doc.id,
            chunks=chunks,
            metadata={"filename": file.filename}
        )
        
        print(f"✅ 文档 {file.filename} 已索引，共 {chunk_count} 个块")
        
        # 3. ✅ 刷新检索器，让新数据立即生效
        global _global_retriever
        _global_retriever = None
        retriever = get_retriever()
        retriever._load_existing_data()
        print("✅ 检索器已刷新")
        
        # 更新文档状态
        await document_service.update_document_status(db, doc.id, "completed", chunk_count)
        
        return DocumentUploadResponse(
            id=doc.id,
            filename=doc.filename,
            status="completed",
            chunk_count=chunk_count,
            created_at=doc.created_at
        )
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        await document_service.update_document_status(db, doc.id, "failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档处理失败: {str(e)}"
        )


@router.get("/", response_model=list[DocumentListResponse])
async def list_documents(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    docs = await document_service.get_user_documents(db, current_user.id)
    return docs
