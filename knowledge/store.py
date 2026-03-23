"""
向量存储模块

使用 ChromaDB 存储和检索文档嵌入
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from core.config import Config


class KnowledgeStore:
    """
    知识库存储类

    使用 ChromaDB 进行向量存储和相似度检索
    """

    def __init__(self, collection_name: str = "knowledge"):
        """
        初始化知识库

        Args:
            collection_name: 集合名称
        """
        # 创建持久化客户端
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIR
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # 使用余弦相似度
        )

    def add_documents(
        self,
        documents: List[str],
        ids: List[str],
        metadatas: List[Dict[str, Any]] = None,
    ):
        """
        添加文档到知识库

        Args:
            documents: 文档内容列表
            ids: 文档 ID 列表
            metadatas: 文档元数据列表
        """
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        搜索相关文档

        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 过滤条件

        Returns:
            Dict: 包含文档、距离、元数据等的搜索结果
        """
        return self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

    def get_document_count(self) -> int:
        """获取文档总数"""
        return self.collection.count()

    def delete_documents(self, ids: List[str]):
        """删除文档"""
        self.collection.delete(ids=ids)

    def clear(self):
        """清空知识库"""
        # 重建集合
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"},
        )
