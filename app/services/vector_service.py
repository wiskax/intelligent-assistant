# app/services/vector_service.py
import os
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import settings

# 修复：使用项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")
# 打印路径以便调试
print(f"📁 ChromaDB 存储路径: {CHROMA_PERSIST_DIR}")

# 初始化嵌入模型
embeddings = OpenAIEmbeddings(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=settings.ZHIPU_API_KEY,
    model="embedding-2"
)


def load_and_split_document(file_path: str, file_type: str):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    doc = Document(page_content=text, metadata={"source": file_path})
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents([doc])
    return [chunk.page_content for chunk in chunks]


def vectorize_and_store(user_id: int, doc_id: int, chunks: list, metadata: dict = None):
    if not chunks:
        return 0
    
    # 确保目录存在
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    
    # 使用 chromadb 原生客户端
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection_name = f"user_{user_id}"
    
    # 删除旧集合（如果存在）
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    # 创建新集合
    collection = client.create_collection(name=collection_name)
    
    # 生成向量
    vectors = embeddings.embed_documents(chunks)
    
    # 准备数据
    ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
    
    # 修复：正确处理 metadata
    metadatas = []
    for i in range(len(chunks)):
        m = {
            "doc_id": doc_id,
            "user_id": user_id,
            "chunk_index": i
        }
        if metadata and isinstance(metadata, dict):
            m["filename"] = metadata.get("filename", "unknown")
        else:
            m["filename"] = "unknown"
        metadatas.append(m)
    
    # 添加到集合
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=vectors,
        metadatas=metadatas
    )
    
    print(f"✅ 已存储 {len(chunks)} 个向量到 {collection_name}")
    return len(chunks)


def search_similar(user_id: int, query: str, top_k: int = 5):
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection_name = f"user_{user_id}"
    
    try:
        collection = client.get_collection(name=collection_name)
    except:
        return []
    
    query_vector = embeddings.embed_query(query)
    
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    
    if not results or not results['documents']:
        return []
    
    return [
        {
            "content": results['documents'][0][i],
            "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
            "score": 1.0 - results['distances'][0][i] if results['distances'] else 0.5
        }
        for i in range(len(results['documents'][0]))
    ]