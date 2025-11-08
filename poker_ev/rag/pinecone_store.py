"""
Pinecone Vector Store for poker.ev RAG system

Simple vector store using Pinecone for poker strategy documents.
"""

import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not installed. Install with: pip install pinecone-client")


class PineconePokerStore:
    """
    Simple Pinecone vector store for poker knowledge

    Uses local sentence-transformers for embeddings (free, no API key needed)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: str = "poker-knowledge",
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384
    ):
        """
        Initialize Pinecone store

        Args:
            api_key: Pinecone API key (or set PINECONE_API_KEY env var)
            index_name: Name for Pinecone index
            embedding_model: SentenceTransformer model name
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone not installed. Run: pip install pinecone-client")

        # Get API key from env if not provided
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            logger.warning(
                "No Pinecone API key found. Set PINECONE_API_KEY environment variable "
                "or pass api_key parameter. Get free API key at: https://www.pinecone.io/"
            )

        self.index_name = index_name
        self.dimension = dimension

        # Initialize embedding model (local, no API needed)
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        # Initialize Pinecone client
        self.pc = None
        self.index = None

        if self.api_key:
            try:
                self.pc = Pinecone(api_key=self.api_key)
                self._init_index()
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")

    def _init_index(self):
        """Create or connect to Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx['name'] for idx in existing_indexes]

            if self.index_name not in index_names:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )

            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")

        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text using local model"""
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def add_documents(self, documents: List[Dict]) -> int:
        """
        Add documents to Pinecone

        Args:
            documents: List of dicts with 'id', 'content', 'metadata'

        Returns:
            Number of documents added
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return 0

        vectors = []
        for doc in documents:
            # Generate embedding
            embedding = self.embed_text(doc['content'])

            # Prepare vector for Pinecone
            vector = {
                'id': doc.get('id', str(hash(doc['content']))),
                'values': embedding,
                'metadata': {
                    'content': doc['content'],
                    **doc.get('metadata', {})
                }
            }
            vectors.append(vector)

        # Upsert to Pinecone
        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"Added {len(vectors)} documents to Pinecone")
            return len(vectors)
        except Exception as e:
            logger.error(f"Error adding documents to Pinecone: {e}")
            return 0

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """
        Search for relevant documents

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of results with content, metadata, and score
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return []

        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)

            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True
            )

            # Format results
            formatted_results = []
            for match in results['matches']:
                formatted_results.append({
                    'content': match['metadata'].get('content', ''),
                    'score': match['score'],
                    'metadata': {k: v for k, v in match['metadata'].items() if k != 'content'}
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []

    def search_as_context(self, query: str, k: int = 3) -> str:
        """
        Search and format results as context string for LLM

        Args:
            query: Search query
            k: Number of results

        Returns:
            Formatted context string
        """
        results = self.search(query, k=k)

        if not results:
            return "No relevant poker strategy information found."

        context_parts = []
        for i, result in enumerate(results, 1):
            category = result['metadata'].get('category', 'Unknown')
            context_parts.append(f"[Source {i}: {category}]")
            context_parts.append(result['content'])
            context_parts.append("")

        return '\n'.join(context_parts)

    def get_stats(self) -> Dict:
        """Get index statistics"""
        if not self.index:
            return {'error': 'Index not initialized'}

        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0)
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}


# Fallback: In-memory store if Pinecone not available
class InMemoryPokerStore:
    """Simple in-memory fallback when Pinecone is not available"""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.documents = []
        logger.info("Using in-memory store (Pinecone not configured)")

    def embed_text(self, text: str) -> List[float]:
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def add_documents(self, documents: List[Dict]) -> int:
        for doc in documents:
            doc['embedding'] = self.embed_text(doc['content'])
            self.documents.append(doc)
        return len(documents)

    def search(self, query: str, k: int = 3) -> List[Dict]:
        if not self.documents:
            return []

        import numpy as np

        # Get query embedding
        query_emb = np.array(self.embed_text(query))

        # Calculate cosine similarity
        scores = []
        for doc in self.documents:
            doc_emb = np.array(doc['embedding'])
            similarity = np.dot(query_emb, doc_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)
            )
            scores.append((similarity, doc))

        # Sort by similarity
        scores.sort(reverse=True, key=lambda x: x[0])

        # Return top k
        results = []
        for score, doc in scores[:k]:
            results.append({
                'content': doc['content'],
                'score': float(score),
                'metadata': doc.get('metadata', {})
            })

        return results

    def search_as_context(self, query: str, k: int = 3) -> str:
        results = self.search(query, k=k)

        if not results:
            return "No relevant poker strategy information found."

        context_parts = []
        for i, result in enumerate(results, 1):
            category = result['metadata'].get('category', 'Unknown')
            context_parts.append(f"[Source {i}: {category}]")
            context_parts.append(result['content'])
            context_parts.append("")

        return '\n'.join(context_parts)

    def get_stats(self) -> Dict:
        return {'total_vectors': len(self.documents), 'mode': 'in-memory'}


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Check if Pinecone API key is set
    if os.getenv("PINECONE_API_KEY"):
        print("✅ Pinecone API key found")
        store = PineconePokerStore()
    else:
        print("⚠️  No Pinecone API key - using in-memory store")
        print("   Set PINECONE_API_KEY env var or get free key at: https://www.pinecone.io/")
        store = InMemoryPokerStore()

    # Test document
    test_docs = [
        {
            'id': 'test1',
            'content': 'Pocket aces (AA) are the strongest starting hand in Texas Hold\'em.',
            'metadata': {'category': 'Hand Rankings'}
        }
    ]

    store.add_documents(test_docs)
    print(f"\n📊 Stats: {store.get_stats()}")

    # Test search
    results = store.search("What is the best starting hand?", k=1)
    print(f"\n🔍 Search results: {len(results)}")
    if results:
        print(f"Top result: {results[0]['content'][:100]}...")
