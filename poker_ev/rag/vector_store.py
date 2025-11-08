"""
Vector Store for poker.ev RAG system

Uses Qdrant in-memory for semantic search of poker strategies.
"""

from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import logging
import uuid

from poker_ev.rag.document_loader import Document, PokerDocumentLoader

logger = logging.getLogger(__name__)


class PokerVectorStore:
    """
    Vector store for poker strategy documents

    Uses Qdrant for vector storage and semantic search.
    Uses sentence-transformers for embeddings.
    """

    def __init__(
        self,
        collection_name: str = "poker_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2",
        in_memory: bool = True
    ):
        """
        Initialize vector store

        Args:
            collection_name: Name for the Qdrant collection
            embedding_model: SentenceTransformer model name
            in_memory: Use in-memory Qdrant (True) or persistent (False)
        """
        self.collection_name = collection_name

        # Initialize Qdrant client
        if in_memory:
            self.client = QdrantClient(":memory:")
            logger.info("Using in-memory Qdrant")
        else:
            self.client = QdrantClient(path="./qdrant_data")
            logger.info("Using persistent Qdrant at ./qdrant_data")

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Create collection if it doesn't exist
        self._create_collection()

    def _create_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def add_documents(self, documents: List[Document]) -> int:
        """
        Add documents to vector store

        Args:
            documents: List of Document objects

        Returns:
            Number of documents added
        """
        if not documents:
            logger.warning("No documents to add")
            return 0

        points = []

        for doc in documents:
            # Generate embedding if not already present
            if doc.embedding is None:
                doc.embedding = self.embed_text(doc.content)

            # Create point for Qdrant
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=doc.embedding,
                payload={
                    'content': doc.content,
                    'metadata': doc.metadata
                }
            )
            points.append(point)

        # Upload to Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Added {len(points)} documents to vector store")
            return len(points)

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(
        self,
        query: str,
        k: int = 3,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search for relevant documents

        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score (0.0 to 1.0)
            filter_metadata: Filter by metadata (e.g., {'category': 'Pot Odds'})

        Returns:
            List of result dicts with 'content', 'metadata', and 'score'
        """
        # Generate query embedding
        query_embedding = self.embed_text(query)

        # Build filter if provided
        qdrant_filter = None
        if filter_metadata:
            # Note: Qdrant filter syntax would go here
            # For simplicity, we'll filter after retrieval
            pass

        try:
            # Search Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=k,
                score_threshold=score_threshold
            )

            # Format results
            results = []
            for hit in search_results:
                result = {
                    'content': hit.payload['content'],
                    'metadata': hit.payload['metadata'],
                    'score': hit.score
                }

                # Apply metadata filter if provided
                if filter_metadata:
                    match = all(
                        result['metadata'].get(key) == value
                        for key, value in filter_metadata.items()
                    )
                    if match:
                        results.append(result)
                else:
                    results.append(result)

            logger.info(f"Search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

    def search_with_context(
        self,
        query: str,
        k: int = 3,
        include_context: bool = True
    ) -> str:
        """
        Search and format results as context for LLM

        Args:
            query: Search query
            k: Number of results
            include_context: Include source metadata

        Returns:
            Formatted context string
        """
        results = self.search(query, k=k)

        if not results:
            return "No relevant information found in the knowledge base."

        # Format results
        context_parts = []

        for i, result in enumerate(results, 1):
            if include_context:
                category = result['metadata'].get('category', 'Unknown')
                context_parts.append(f"[Source {i}: {category}]")

            context_parts.append(result['content'])
            context_parts.append("")  # Empty line between results

        return '\n'.join(context_parts)

    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection

        Returns:
            Dict with collection statistics
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'collection_name': self.collection_name,
                'points_count': collection_info.points_count,
                'vectors_count': collection_info.vectors_count,
                'status': collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    def clear_collection(self):
        """Delete all documents from collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self._create_collection()
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")

    def initialize_from_knowledge_base(self) -> int:
        """
        Load and index all documents from knowledge base

        Returns:
            Number of documents indexed
        """
        loader = PokerDocumentLoader()
        documents = loader.load_all_documents()

        if not documents:
            logger.warning("No documents loaded from knowledge base")
            return 0

        return self.add_documents(documents)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create vector store
    print("🔧 Initializing vector store...")
    vector_store = PokerVectorStore()

    # Load poker knowledge base
    print("\n📚 Loading poker knowledge base...")
    num_docs = vector_store.initialize_from_knowledge_base()
    print(f"✅ Indexed {num_docs} document chunks")

    # Get stats
    stats = vector_store.get_collection_stats()
    print(f"\n📊 Collection stats:")
    print(f"  • Points: {stats.get('points_count', 0)}")
    print(f"  • Status: {stats.get('status', 'unknown')}")

    # Test search
    print("\n🔍 Testing search...")
    query = "What are pot odds and how do I calculate them?"
    results = vector_store.search(query, k=2)

    print(f"\nQuery: {query}")
    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   Category: {result['metadata']['category']}")
        print(f"   Preview: {result['content'][:150]}...\n")

    # Test formatted context
    print("\n📝 Formatted context for LLM:")
    context = vector_store.search_with_context(query, k=2)
    print(context[:500] + "...")
