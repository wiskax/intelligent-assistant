# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = Field(alias="DATABASE_URL", default="postgresql+asyncpg://postgres:postgres@localhost:5432/intelligent_assistant")
    
    # JWT
    SECRET_KEY: str = Field(alias="SECRET_KEY", default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(alias="ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    
    # LLM
    ZHIPU_API_KEY: str = Field(alias="ZHIPU_API_KEY", default="")
    
    # Redis
    REDIS_URL: str = Field(alias="REDIS_URL", default="redis://localhost:6379/0")
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = Field(alias="CHROMA_PERSIST_DIR", default="./chroma_db")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()