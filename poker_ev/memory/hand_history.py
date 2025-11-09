"""
Hand History Storage for poker.ev

Stores and retrieves poker hand history using Pinecone vector database.
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

from poker_ev.memory.pinecone_store import PineconeMemoryStore

logger = logging.getLogger(__name__)


class HandHistory:
    """
    Stores and manages poker hand history using Pinecone

    Provides semantic search capabilities for finding similar hands
    and pattern recognition.
    """

    def __init__(self, pinecone_store: Optional[PineconeMemoryStore] = None):
        """
        Initialize hand history storage

        Args:
            pinecone_store: PineconeMemoryStore instance (creates new if None)
        """
        if pinecone_store is None:
            try:
                self.store = PineconeMemoryStore()
                logger.info("Hand history initialized with new Pinecone store")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone store: {e}")
                raise
        else:
            self.store = pinecone_store
            logger.info("Hand history initialized with provided Pinecone store")

    def save_hand(self, hand_data: Dict) -> bool:
        """
        Save a hand to history

        Args:
            hand_data: Dictionary with hand information
                Required keys: hand_id, your_cards, pot, outcome
                Optional keys: board, actions, actions_summary, winner, profit,
                             phase, position, notes, hand_strength, board_texture,
                             opponent_style, aggression_level

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in hand_data:
                hand_data['timestamp'] = datetime.now().isoformat()

            # Save to Pinecone
            success = self.store.save_hand(hand_data)

            if success:
                logger.debug(f"Saved hand {hand_data.get('hand_id')}")
            else:
                logger.warning(f"Failed to save hand {hand_data.get('hand_id')}")

            return success

        except Exception as e:
            logger.error(f"Error saving hand: {e}")
            return False

    def get_recent_hands(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent hands

        Args:
            limit: Maximum number of hands to return

        Returns:
            List of hand dictionaries
        """
        try:
            results = self.store.get_recent_hands(limit=limit)

            # Convert from search results format to hand dict format
            hands = []
            for result in results:
                hand = result.get('metadata', {})
                hand['score'] = result.get('score')
                hands.append(hand)

            return hands

        except Exception as e:
            logger.error(f"Error getting recent hands: {e}")
            return []

    def search_similar_hands(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for hands similar to the query using semantic search

        Args:
            query: Search query (e.g., "pocket aces against aggressive opponent")
            limit: Maximum number of hands to return
            filters: Additional Pinecone filters (e.g., {"outcome": "won"})

        Returns:
            List of matching hand dictionaries with similarity scores
        """
        try:
            # Build filter dict
            filter_dict = {"type": "hand"}
            if filters:
                filter_dict.update(filters)

            # Search
            results = self.store.search(
                query=query,
                filter_dict=filter_dict,
                top_k=limit
            )

            # Convert to hand dicts
            hands = []
            for result in results:
                hand = result.get('metadata', {})
                hand['similarity_score'] = result.get('score')
                hands.append(hand)

            logger.debug(f"Found {len(hands)} similar hands for query: '{query}'")
            return hands

        except Exception as e:
            logger.error(f"Error searching similar hands: {e}")
            return []

    def get_hands_by_outcome(self, outcome: str, limit: int = 100) -> List[Dict]:
        """
        Get hands filtered by outcome

        Args:
            outcome: Outcome to filter by ('won', 'lost', 'folded')
            limit: Maximum number of hands to return

        Returns:
            List of matching hand dictionaries
        """
        try:
            # Use semantic search with outcome filter
            results = self.store.search(
                query=f"poker hands with outcome {outcome}",
                filter_dict={"type": "hand", "outcome": outcome},
                top_k=limit
            )

            # Convert to hand dicts
            hands = []
            for result in results:
                hand = result.get('metadata', {})
                hands.append(hand)

            return hands

        except Exception as e:
            logger.error(f"Error getting hands by outcome: {e}")
            return []

    def get_hands_by_position(self, position: str, limit: int = 100) -> List[Dict]:
        """
        Get hands filtered by position

        Args:
            position: Position to filter by (e.g., 'Button', 'Big Blind')
            limit: Maximum number of hands to return

        Returns:
            List of matching hand dictionaries
        """
        try:
            results = self.store.search(
                query=f"poker hands from {position} position",
                filter_dict={"type": "hand", "position": position},
                top_k=limit
            )

            hands = []
            for result in results:
                hand = result.get('metadata', {})
                hands.append(hand)

            return hands

        except Exception as e:
            logger.error(f"Error getting hands by position: {e}")
            return []

    def get_statistics(self) -> Dict:
        """
        Get overall statistics from all hands

        Returns:
            Dictionary with statistics
        """
        try:
            # Get all hands (up to 1000 for statistics)
            all_hands = self.get_recent_hands(limit=1000)

            if not all_hands:
                return {
                    'total_hands': 0,
                    'outcomes': {},
                    'total_profit': 0,
                    'avg_profit': 0.0,
                    'win_rate': 0.0
                }

            # Calculate statistics
            total_hands = len(all_hands)
            outcome_counts = {}
            total_profit = 0

            for hand in all_hands:
                # Count outcomes
                outcome = hand.get('outcome', 'unknown')
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

                # Sum profit
                profit = hand.get('profit', 0)
                if isinstance(profit, (int, float)):
                    total_profit += profit

            # Calculate rates
            avg_profit = total_profit / total_hands if total_hands > 0 else 0
            wins = outcome_counts.get('won', 0)
            win_rate = (wins / total_hands * 100) if total_hands > 0 else 0

            return {
                'total_hands': total_hands,
                'outcomes': outcome_counts,
                'total_profit': total_profit,
                'avg_profit': round(avg_profit, 2),
                'win_rate': round(win_rate, 2)
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def find_patterns(self, description: str, limit: int = 5) -> List[Dict]:
        """
        Find hands matching a pattern description using semantic search

        Args:
            description: Pattern description (e.g., "bluffing on the river")
            limit: Maximum number of hands to return

        Returns:
            List of matching hands
        """
        return self.search_similar_hands(query=description, limit=limit)

    def get_context_for_current_hand(
        self,
        current_hand: Dict,
        limit: int = 3
    ) -> List[Dict]:
        """
        Get relevant context from hand history for current hand

        Args:
            current_hand: Current hand data (cards, position, etc.)
            limit: Number of similar hands to retrieve

        Returns:
            List of similar hands from history
        """
        try:
            # Build query from current hand
            cards = current_hand.get('your_cards', [])
            position = current_hand.get('position', '')
            board = current_hand.get('board', [])

            cards_str = ', '.join(cards) if isinstance(cards, list) else str(cards)
            board_str = ', '.join(board) if isinstance(board, list) else str(board)

            query = f"Hand: {cards_str}, Position: {position}"
            if board_str:
                query += f", Board: {board_str}"

            # Search for similar hands
            similar_hands = self.search_similar_hands(query=query, limit=limit)

            logger.debug(f"Found {len(similar_hands)} similar hands for current situation")
            return similar_hands

        except Exception as e:
            logger.error(f"Error getting context for current hand: {e}")
            return []

    def clear_history(self) -> bool:
        """
        Clear all hand history

        Note: This is not fully implemented in PineconeMemoryStore yet.

        Returns:
            True if cleared successfully
        """
        try:
            # This would require listing all hand IDs and deleting them
            logger.warning("clear_history not fully implemented for Pinecone yet")
            return False

        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create hand history
    try:
        history = HandHistory()
        print("✅ Hand history initialized with Pinecone")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        exit(1)

    # Example hand data
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
    if history.save_hand(example_hand):
        print("✅ Hand saved successfully")

    # Get statistics
    stats = history.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  • Total hands: {stats['total_hands']}")
    print(f"  • Win rate: {stats['win_rate']}%")
    print(f"  • Total profit: ${stats['total_profit']}")
    print(f"  • Avg profit/hand: ${stats['avg_profit']}")

    # Search for similar hands
    print("\n🔍 Searching for similar hands...")
    similar = history.search_similar_hands("aggressive play with premium hands", limit=3)
    print(f"Found {len(similar)} similar hands:")
    for hand in similar:
        print(f"  • {hand.get('hand_id')}: {hand.get('outcome')} (score: {hand.get('similarity_score', 0):.3f})")

    # Get recent hands
    recent = history.get_recent_hands(limit=5)
    print(f"\n📋 Recent hands: {len(recent)}")
    for hand in recent:
        print(f"  • {hand.get('hand_id')}: {hand.get('outcome')} (${hand.get('profit')})")
