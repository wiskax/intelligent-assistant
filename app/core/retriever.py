# app/core/retriever.py
import re
import os
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import numpy as np
from langchain_openai import OpenAIEmbeddings
from app.config import settings


class HybridRetriever:
    """
    混合检索器：结合 BM25 关键词检索 + 向量语义检索
    """

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            base_url="https://open.bigmodel.cn/api/paas/v4",
            api_key=settings.ZHIPU_API_KEY,
            model="embedding-2"
        )
        self.chunks: List[str] = []
        self.metadatas: List[Dict] = []
        self.bm25: BM25Okapi = None
        self.vectors: np.ndarray = None
        # 启动时自动加载已有数据
        self._load_existing_data()

    def _load_existing_data(self):
        """从 chroma_db 加载已有的向量数据"""
        chroma_dir = "./chroma_db"
        if not os.path.exists(chroma_dir):
            print("ℹ️ chroma_db 不存在，跳过加载")
            return

        try:
            import chromadb
            client = chromadb.PersistentClient(chroma_dir)
            collections = client.list_collections()
            
            if not collections:
                print("ℹ️ chroma_db 为空，跳过加载")
                return

            all_chunks = []
            all_metadatas = []

            for collection in collections:
                try:
                    # 获取集合中的所有数据
                    results = collection.get()
                    if results and results.get('documents'):
                        chunks = results['documents']
                        metadatas = results['metadatas']
                        
                        # 转换为列表
                        if isinstance(chunks, list):
                            all_chunks.extend(chunks)
                            all_metadatas.extend(metadatas)
                            print(f"✅ 从集合 {collection.name} 加载了 {len(chunks)} 个文档")
                except Exception as e:
                    print(f"⚠️ 加载集合 {collection.name} 失败: {e}")

            if all_chunks:
                # 重建 BM25 索引
                tokenized_chunks = [self._tokenize(chunk) for chunk in all_chunks]
                self.bm25 = BM25Okapi(tokenized_chunks)
                
                # 重建向量索引
                if all_chunks:
                    self.vectors = self.embeddings.embed_documents(all_chunks)
                    self.vectors = np.array(self.vectors)
                
                self.chunks = all_chunks
                self.metadatas = all_metadatas
                print(f"✅ 总共加载了 {len(all_chunks)} 个文档块")
            else:
                print("ℹ️ 没有加载到任何数据")

        except Exception as e:
            print(f"⚠️ 加载 chroma_db 失败: {e}")

    def add_documents(self, chunks: List[str], metadatas: List[Dict]):
        """添加文档块到检索器"""
        print(f"📝 添加 {len(chunks)} 个文档到检索器")
        self.chunks = chunks
        self.metadatas = metadatas

        tokenized_chunks = [self._tokenize(chunk) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_chunks)

        if chunks:
            self.vectors = self.embeddings.embed_documents(chunks)
            self.vectors = np.array(self.vectors)
            print(f"✅ 向量化完成，维度: {self.vectors.shape}")

    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'[，、。！？；：""''（）\n\t]', ' ', text)
        tokens = [t for t in text.split() if t.strip()]
        if not tokens:
            tokens = list(text)
        return tokens

    def _tokenize_query(self, query: str) -> List[str]:
        return self._tokenize(query)

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        if not self.chunks or len(self.chunks) == 0:
            return []

        tokenized_query = self._tokenize_query(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)

        query_vector = self.embeddings.embed_query(query)
        query_vector = np.array(query_vector)

        normalized_vectors = self.vectors / np.linalg.norm(self.vectors, axis=1, keepdims=True)
        normalized_query = query_vector / np.linalg.norm(query_vector)
        similarity_scores = np.dot(normalized_vectors, normalized_query)

        bm25_norm = self._normalize_scores(bm25_scores)
        vector_norm = self._normalize_scores(similarity_scores)

        combined_scores = alpha * vector_norm + (1 - alpha) * bm25_norm

        top_indices = np.argsort(combined_scores)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                "chunk": self.chunks[idx],
                "metadata": self.metadatas[idx],
                "score": float(combined_scores[idx]),
                "bm25_score": float(bm25_scores[idx]),
                "vector_score": float(similarity_scores[idx])
            })

        return results

    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        if np.max(scores) - np.min(scores) == 0:
            return np.zeros_like(scores)
        return (scores - np.min(scores)) / (np.max(scores) - np.min(scores))


# ========== 全局检索器实例 ==========
_global_retriever: HybridRetriever = None


def get_retriever() -> HybridRetriever:
    """获取全局检索器实例（单例模式）"""
    global _global_retriever
    if _global_retriever is None:
        _global_retriever = HybridRetriever()
    return _global_retriever