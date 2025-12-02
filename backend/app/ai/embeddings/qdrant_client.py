"""
Qdrant Client for Vector Storage
Manages message embeddings in Qdrant vector database.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

from app.ai.config import get_ai_config


class QdrantManager:
    """
    Manages Qdrant vector database operations for message embeddings.
    Implements the vector storage requirements from the design document.
    """
    
    COLLECTION_NAME = "message_embeddings"
    VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small dimension
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Qdrant client
        
        Args:
            url: Qdrant server URL (defaults to QDRANT_URL env var)
            api_key: Qdrant API key (defaults to QDRANT_API_KEY env var)
        """
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key if self.api_key else None
        )
        
        # Get embeddings model
        ai_config = get_ai_config()
        self.embeddings = ai_config.get_embeddings()
        
        # Initialize collection if it doesn't exist
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self) -> None:
        """
        Ensure the message embeddings collection exists in Qdrant.
        Creates it if it doesn't exist.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.COLLECTION_NAME not in collection_names:
                # Create collection with cosine distance
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            # Log error but don't fail initialization
            print(f"Error ensuring collection exists: {e}")
    
    def get_vector_store(self) -> QdrantVectorStore:
        """
        Get LangChain QdrantVectorStore instance
        
        Returns:
            QdrantVectorStore: LangChain vector store for the collection
        """
        return QdrantVectorStore(
            client=self.client,
            collection_name=self.COLLECTION_NAME,
            embedding=self.embeddings
        )
    
    async def store_message_embedding(
        self,
        message_id: str,
        user_id: str,
        platform: str,
        content: str,
        timestamp: datetime,
        subject: Optional[str] = None
    ) -> str:
        """
        Generate and store embedding for a message
        
        Args:
            message_id: Unique message identifier
            user_id: User who owns the message
            platform: Source platform (gmail, slack, calendar)
            content: Message content to embed
            timestamp: Message timestamp
            subject: Optional message subject
        
        Returns:
            str: Point ID in Qdrant
        """
        # Generate embedding
        embedding = await self.embeddings.aembed_query(content)
        
        # Create content preview (first 200 chars)
        content_preview = content[:200] + "..." if len(content) > 200 else content
        
        # Create payload with metadata
        payload = {
            "message_id": message_id,
            "user_id": user_id,
            "platform": platform,
            "timestamp": int(timestamp.timestamp()),
            "content_preview": content_preview
        }
        
        if subject:
            payload["subject"] = subject
        
        # Store in Qdrant
        point = PointStruct(
            id=message_id,  # Use message_id as point ID for easy lookup
            vector=embedding,
            payload=payload
        )
        
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point]
        )
        
        return message_id
    
    async def semantic_search(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search over message embeddings
        
        Args:
            query: Search query text
            user_id: User ID to filter results
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0.0 to 1.0)
        
        Returns:
            List[Dict[str, Any]]: List of search results with message_id and metadata
        """
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Search in Qdrant with user filter
        search_results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter={
                "must": [
                    {
                        "key": "user_id",
                        "match": {"value": user_id}
                    }
                ]
            },
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "message_id": result.payload.get("message_id"),
                "user_id": result.payload.get("user_id"),
                "platform": result.payload.get("platform"),
                "timestamp": result.payload.get("timestamp"),
                "content_preview": result.payload.get("content_preview"),
                "subject": result.payload.get("subject"),
                "score": result.score
            })
        
        return results
    
    async def delete_message_embedding(self, message_id: str) -> bool:
        """
        Delete a message embedding from Qdrant
        
        Args:
            message_id: Message ID to delete
        
        Returns:
            bool: True if successful
        """
        try:
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=[message_id]
            )
            return True
        except Exception as e:
            print(f"Error deleting message embedding: {e}")
            return False
    
    async def delete_user_embeddings(self, user_id: str) -> bool:
        """
        Delete all embeddings for a user
        
        Args:
            user_id: User ID whose embeddings to delete
        
        Returns:
            bool: True if successful
        """
        try:
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector={
                    "filter": {
                        "must": [
                            {
                                "key": "user_id",
                                "match": {"value": user_id}
                            }
                        ]
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Error deleting user embeddings: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the message embeddings collection
        
        Returns:
            Dict[str, Any]: Collection information including count and config
        """
        try:
            collection_info = self.client.get_collection(self.COLLECTION_NAME)
            return {
                "name": collection_info.config.params.vectors.size,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "points_count": collection_info.points_count
            }
        except Exception as e:
            return {"error": str(e)}


# Global Qdrant manager instance
_qdrant_manager: Optional[QdrantManager] = None


def get_qdrant_manager() -> QdrantManager:
    """
    Get or create global Qdrant manager instance
    
    Returns:
        QdrantManager: Global Qdrant manager
    """
    global _qdrant_manager
    if _qdrant_manager is None:
        _qdrant_manager = QdrantManager()
    return _qdrant_manager


def set_qdrant_manager(manager: QdrantManager) -> None:
    """
    Set global Qdrant manager instance
    
    Args:
        manager: Qdrant manager to set
    """
    global _qdrant_manager
    _qdrant_manager = manager


# Alias for backward compatibility
get_qdrant_client = get_qdrant_manager
