"""
Vector Storage Module

Uses ChromaDB to store and retrieve document embeddings
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from core.config import Config


class KnowledgeStore:
    """
    Knowledge base storage class

    Uses ChromaDB for vector storage and similarity retrieval
    """

    def __init__(self, collection_name: str = "knowledge"):
        """
        Initialize knowledge base

        Args:
            collection_name: Collection name
        """
        # Create persistent client
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIR
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )

    def add_documents(
        self,
        documents: List[str],
        ids: List[str],
        metadatas: List[Dict[str, Any]] = None,
    ):
        """
        Add documents to knowledge base

        Args:
            documents: List of document content
            ids: List of document IDs
            metadatas: List of document metadata
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
        Search for relevant documents

        Args:
            query: Query text
            n_results: Number of results to return
            where: Filter conditions

        Returns:
            Dict: Search results containing documents, distances, metadata, etc.
        """
        return self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

    def get_document_count(self) -> int:
        """Get total document count"""
        return self.collection.count()

    def delete_documents(self, ids: List[str]):
        """Delete documents"""
        self.collection.delete(ids=ids)

    def clear(self):
        """Clear knowledge base"""
        # Recreate collection
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"},
        )
