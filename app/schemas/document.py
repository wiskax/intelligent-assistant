# app/schemas/document.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    status: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: int
    filename: str
    status: str
    chunk_count: int
    created_at: datetime
    vectorized: bool = True  # 新增
    class Config:
        from_attributes = True