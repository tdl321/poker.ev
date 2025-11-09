"""
Pinecone Memory Store for poker.ev

Semantic memory storage for hands, patterns, sessions, and opponent profiles.
"""

import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

logger = logging.getLogger(__name__)


class PineconeMemoryStore:
    """
    Vector-based memory storage using Pinecone

    Stores:
    - Hand history with semantic search
    - Pattern recognition across hands
    - Chat session memories
    - Opponent profiles
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: str = "poker-memory",
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384
    ):
        """
        Initialize Pinecone memory store

        Args:
            api_key: Pinecone API key (reads from env if None)
            index_name: Name of Pinecone index
            embedding_model: SentenceTransformer model name
            dimension: Embedding dimension (must match model)
        """
        self.index_name = index_name
        self.dimension = dimension

        # Get API key
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("No Pinecone API key found. Set PINECONE_API_KEY environment variable.")

        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=self.api_key)
            logger.info("Pinecone client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise

        # Initialize embedding model
        try:
            self.embedder = SentenceTransformer(embedding_model)
            logger.info(f"Embedding model loaded: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

        # Initialize index
        self.index = self._init_index()

    def _init_index(self):
        """Create or connect to Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]

            if self.index_name not in index_names:
                logger.info(f"Creating new index: {self.index_name}")

                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.info(f"Index '{self.index_name}' created successfully")
            else:
                logger.info(f"Index '{self.index_name}' already exists")

            # Connect to index
            index = self.pc.Index(self.index_name)
            logger.info(f"Connected to index '{self.index_name}'")

            return index

        except Exception as e:
            logger.error(f"Error initializing index: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            embedding = self.embedder.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def _create_hand_description(self, hand_data: Dict) -> str:
        """
        Create semantic description of a hand for embedding

        Args:
            hand_data: Hand information

        Returns:
            Description string
        """
        parts = []

        # Cards
        cards = hand_data.get('your_cards', [])
        if isinstance(cards, list):
            cards_str = ', '.join(cards)
        else:
            cards_str = str(cards)
        parts.append(f"Hand: {cards_str}")

        # Position
        position = hand_data.get('position', 'unknown')
        parts.append(f"Position: {position}")

        # Actions
        actions = hand_data.get('actions_summary', '')
        if actions:
            parts.append(f"Actions: {actions}")

        # Board
        board = hand_data.get('board', [])
        if board:
            if isinstance(board, list):
                board_str = ', '.join(board)
            else:
                board_str = str(board)
            parts.append(f"Board: {board_str}")

        # Outcome
        outcome = hand_data.get('outcome', 'unknown')
        profit = hand_data.get('profit', 0)
        parts.append(f"Outcome: {outcome}, Profit: ${profit}")

        # Notes
        notes = hand_data.get('notes', '')
        if notes:
            parts.append(f"Notes: {notes}")

        return ". ".join(parts)

    def save_hand(self, hand_data: Dict) -> bool:
        """
        Save a hand to Pinecone with semantic embedding

        Args:
            hand_data: Hand information
                Required: hand_id, your_cards, pot, outcome
                Optional: board, actions, actions_summary, winner, profit,
                         phase, position, notes, hand_strength, board_texture,
                         opponent_style, aggression_level

        Returns:
            True if saved successfully
        """
        try:
            hand_id = hand_data.get('hand_id')
            if not hand_id:
                logger.error("Hand data missing hand_id")
                return False

            # Add timestamp if not present
            if 'timestamp' not in hand_data:
                hand_data['timestamp'] = datetime.now().isoformat()

            # Create semantic description
            description = self._create_hand_description(hand_data)

            # Generate embedding
            embedding = self.embed_text(description)

            # Prepare metadata (Pinecone only supports simple types)
            metadata = {
                'hand_id': hand_id,
                'timestamp': hand_data['timestamp'],
                'type': 'hand',
                'description': description,

                # Convert complex fields to JSON strings
                'your_cards': json.dumps(hand_data.get('your_cards', [])),
                'board': json.dumps(hand_data.get('board', [])),
                'actions': json.dumps(hand_data.get('actions', [])),

                # Simple fields
                'pot': int(hand_data.get('pot', 0)),
                'winner': int(hand_data.get('winner', -1)) if hand_data.get('winner') is not None else -1,
                'outcome': hand_data.get('outcome', 'unknown'),
                'profit': int(hand_data.get('profit', 0)),
                'phase': hand_data.get('phase', 'unknown'),
                'position': hand_data.get('position', 'unknown'),
                'notes': hand_data.get('notes', ''),

                # Optional contextual fields
                'hand_strength': hand_data.get('hand_strength', ''),
                'board_texture': hand_data.get('board_texture', ''),
                'opponent_style': hand_data.get('opponent_style', ''),
                'aggression_level': hand_data.get('aggression_level', ''),
                'actions_summary': hand_data.get('actions_summary', '')
            }

            # Remove empty strings to save space
            metadata = {k: v for k, v in metadata.items() if v != ''}

            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(f"hand_{hand_id}", embedding, metadata)]
            )

            logger.debug(f"Saved hand {hand_id} to Pinecone")
            return True

        except Exception as e:
            logger.error(f"Error saving hand: {e}")
            return False

    def save_pattern(self, pattern_data: Dict) -> bool:
        """
        Save a pattern to Pinecone

        Args:
            pattern_data: Pattern information
                Required: pattern_id, pattern_name, description
                Optional: category, frequency, win_rate, avg_profit,
                         positions, actions, success, hand_ids, insight

        Returns:
            True if saved successfully
        """
        try:
            pattern_id = pattern_data.get('pattern_id')
            if not pattern_id:
                logger.error("Pattern data missing pattern_id")
                return False

            # Create description for embedding
            description = pattern_data.get('description', '')
            pattern_name = pattern_data.get('pattern_name', '')
            insight = pattern_data.get('insight', '')

            full_description = f"{pattern_name}. {description}. {insight}"

            # Generate embedding
            embedding = self.embed_text(full_description)

            # Prepare metadata
            metadata = {
                'pattern_id': pattern_id,
                'type': 'pattern',
                'pattern_name': pattern_name,
                'description': description,
                'category': pattern_data.get('category', ''),
                'frequency': int(pattern_data.get('frequency', 0)),
                'win_rate': float(pattern_data.get('win_rate', 0.0)),
                'avg_profit': float(pattern_data.get('avg_profit', 0.0)),
                'positions': json.dumps(pattern_data.get('positions', [])),
                'actions': json.dumps(pattern_data.get('actions', [])),
                'success': bool(pattern_data.get('success', False)),
                'hand_ids': json.dumps(pattern_data.get('hand_ids', [])),
                'insight': insight,
                'timestamp': pattern_data.get('timestamp', datetime.now().isoformat())
            }

            # Remove empty strings
            metadata = {k: v for k, v in metadata.items() if v != '' and v is not None}

            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(f"pattern_{pattern_id}", embedding, metadata)]
            )

            logger.debug(f"Saved pattern {pattern_id} to Pinecone")
            return True

        except Exception as e:
            logger.error(f"Error saving pattern: {e}")
            return False

    def save_session(self, session_data: Dict) -> bool:
        """
        Save a chat session to Pinecone

        Args:
            session_data: Session information
                Required: session_id, summary
                Optional: topics, advice_given, hands_discussed,
                         user_questions, message_count, duration_minutes

        Returns:
            True if saved successfully
        """
        try:
            session_id = session_data.get('session_id')
            if not session_id:
                logger.error("Session data missing session_id")
                return False

            # Create description
            summary = session_data.get('summary', '')
            topics = session_data.get('topics', [])
            topics_str = ', '.join(topics) if topics else ''

            description = f"Session summary: {summary}. Topics: {topics_str}"

            # Generate embedding
            embedding = self.embed_text(description)

            # Prepare metadata
            metadata = {
                'session_id': session_id,
                'type': 'session',
                'summary': summary,
                'topics': json.dumps(topics),
                'advice_given': json.dumps(session_data.get('advice_given', [])),
                'hands_discussed': json.dumps(session_data.get('hands_discussed', [])),
                'user_questions': json.dumps(session_data.get('user_questions', [])),
                'message_count': int(session_data.get('message_count', 0)),
                'duration_minutes': int(session_data.get('duration_minutes', 0)),
                'timestamp': session_data.get('timestamp', datetime.now().isoformat())
            }

            # Remove empty values
            metadata = {k: v for k, v in metadata.items() if v not in ('', [], None)}

            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(f"session_{session_id}", embedding, metadata)]
            )

            logger.debug(f"Saved session {session_id} to Pinecone")
            return True

        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    def search(
        self,
        query: str,
        filter_dict: Optional[Dict] = None,
        top_k: int = 5,
        include_metadata: bool = True
    ) -> List[Dict]:
        """
        Semantic search across memory

        Args:
            query: Search query
            filter_dict: Pinecone metadata filter (e.g., {"type": "hand"})
            top_k: Number of results to return
            include_metadata: Whether to include metadata in results

        Returns:
            List of matching results with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)

            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                filter=filter_dict,
                top_k=top_k,
                include_metadata=include_metadata
            )

            # Format results
            formatted_results = []
            for match in results.matches:
                result = {
                    'id': match.id,
                    'score': float(match.score),
                }

                if include_metadata:
                    metadata = dict(match.metadata)

                    # Parse JSON fields back to objects
                    for key in ['your_cards', 'board', 'actions', 'positions',
                               'topics', 'advice_given', 'hands_discussed',
                               'user_questions', 'hand_ids']:
                        if key in metadata:
                            try:
                                metadata[key] = json.loads(metadata[key])
                            except:
                                pass

                    result['metadata'] = metadata

                formatted_results.append(result)

            logger.debug(f"Search query '{query}' returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []

    def search_hands(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar hands"""
        return self.search(
            query=query,
            filter_dict={"type": "hand"},
            top_k=top_k
        )

    def search_patterns(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for patterns"""
        return self.search(
            query=query,
            filter_dict={"type": "pattern"},
            top_k=top_k
        )

    def search_sessions(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for chat sessions"""
        return self.search(
            query=query,
            filter_dict={"type": "session"},
            top_k=top_k
        )

    def get_recent_hands(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent hands (by timestamp in metadata)

        Note: This uses a dummy query to retrieve hands, then sorts by timestamp.
        Not the most efficient for large datasets, but works for now.

        Args:
            limit: Maximum number of hands to return

        Returns:
            List of recent hands
        """
        try:
            # Query for hands with high limit
            results = self.search(
                query="poker hand",
                filter_dict={"type": "hand"},
                top_k=min(limit * 2, 100)  # Get more than needed
            )

            # Sort by timestamp
            sorted_results = sorted(
                results,
                key=lambda x: x['metadata'].get('timestamp', ''),
                reverse=True
            )

            return sorted_results[:limit]

        except Exception as e:
            logger.error(f"Error getting recent hands: {e}")
            return []

    def get_stats(self) -> Dict:
        """
        Get memory store statistics

        Returns:
            Dictionary with stats
        """
        try:
            stats = self.index.describe_index_stats()

            # Get counts by type
            type_counts = {}
            for namespace_stats in [stats.namespaces.get('', {})]:
                if hasattr(namespace_stats, 'vector_count'):
                    total_vectors = namespace_stats.vector_count
                else:
                    total_vectors = stats.total_vector_count

            return {
                'total_vectors': total_vectors,
                'dimension': self.dimension,
                'index_name': self.index_name
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    def clear_type(self, memory_type: str) -> bool:
        """
        Clear all memories of a specific type

        Args:
            memory_type: Type to clear ('hand', 'pattern', 'session')

        Returns:
            True if cleared successfully
        """
        try:
            # This is tricky with Pinecone - we'd need to list all IDs with the type filter
            # and delete them. For now, we'll skip this implementation.
            logger.warning("clear_type not fully implemented yet")
            return False

        except Exception as e:
            logger.error(f"Error clearing type {memory_type}: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create memory store
    try:
        memory = PineconeMemoryStore()
        print("✅ Pinecone memory store initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        exit(1)

    # Example hand
    example_hand = {
        'hand_id': 'test_hand_001',
        'your_cards': ['A♠', 'K♥'],
        'board': ['Q♥', 'J♦', '10♣', '9♠', '2♥'],
        'actions_summary': 'Raised preflop, bet flop, called turn, bet river',
        'pot': 150,
        'winner': 0,
        'outcome': 'won',
        'profit': 75,
        'phase': 'RIVER',
        'position': 'Button',
        'hand_strength': 'straight',
        'board_texture': 'connected',
        'opponent_style': 'tight',
        'aggression_level': 'aggressive',
        'notes': 'Good aggressive play with straight'
    }

    # Save hand
    print("\n💾 Saving example hand...")
    if memory.save_hand(example_hand):
        print("✅ Hand saved successfully")

    # Search for similar hands
    print("\n🔍 Searching for similar hands...")
    results = memory.search_hands("pocket aces, aggressive play", top_k=3)
    print(f"Found {len(results)} similar hands:")
    for result in results:
        print(f"  • {result['id']} (score: {result['score']:.3f})")
        print(f"    {result['metadata'].get('description', 'N/A')[:80]}...")

    # Get stats
    print("\n📊 Memory stats:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  • {key}: {value}")
