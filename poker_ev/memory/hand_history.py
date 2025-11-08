"""
Hand History Storage for poker.ev

Stores and retrieves poker hand history for analysis and learning.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HandHistory:
    """
    Stores and manages poker hand history

    Uses SQLite for persistent storage of hand data.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize hand history storage

        Args:
            db_path: Path to SQLite database file (None for default)
        """
        if db_path is None:
            # Default to poker_ev/memory/hand_history.db
            db_path = Path(__file__).parent / "hand_history.db"

        self.db_path = str(db_path)
        self._init_database()

    def _init_database(self):
        """Create database and tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create hands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hands (
                    hand_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    your_cards TEXT NOT NULL,
                    board TEXT,
                    actions TEXT,
                    pot INTEGER,
                    winner INTEGER,
                    outcome TEXT,
                    profit INTEGER,
                    phase TEXT,
                    position TEXT,
                    notes TEXT
                )
            ''')

            # Create index on timestamp
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON hands(timestamp DESC)
            ''')

            # Create index on outcome
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_outcome
                ON hands(outcome)
            ''')

            conn.commit()
            conn.close()

            logger.info(f"Hand history database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def save_hand(self, hand_data: Dict) -> bool:
        """
        Save a hand to history

        Args:
            hand_data: Dictionary with hand information
                Required keys: hand_id, your_cards, pot, outcome
                Optional keys: board, actions, winner, profit, phase, position, notes

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in hand_data:
                hand_data['timestamp'] = datetime.now().isoformat()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert lists/dicts to JSON strings
            your_cards = json.dumps(hand_data.get('your_cards', []))
            board = json.dumps(hand_data.get('board', []))
            actions = json.dumps(hand_data.get('actions', []))

            cursor.execute('''
                INSERT OR REPLACE INTO hands
                (hand_id, timestamp, your_cards, board, actions, pot, winner,
                 outcome, profit, phase, position, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                hand_data['hand_id'],
                hand_data['timestamp'],
                your_cards,
                board,
                actions,
                hand_data.get('pot', 0),
                hand_data.get('winner'),
                hand_data.get('outcome', 'unknown'),
                hand_data.get('profit', 0),
                hand_data.get('phase', 'unknown'),
                hand_data.get('position', 'unknown'),
                hand_data.get('notes', '')
            ))

            conn.commit()
            conn.close()

            logger.debug(f"Saved hand {hand_data['hand_id']}")
            return True

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
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dicts
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM hands
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            rows = cursor.fetchall()
            conn.close()

            # Convert to dicts and parse JSON fields
            hands = []
            for row in rows:
                hand = dict(row)
                hand['your_cards'] = json.loads(hand['your_cards'])
                hand['board'] = json.loads(hand['board']) if hand['board'] else []
                hand['actions'] = json.loads(hand['actions']) if hand['actions'] else []
                hands.append(hand)

            return hands

        except Exception as e:
            logger.error(f"Error getting recent hands: {e}")
            return []

    def get_hands_by_outcome(self, outcome: str) -> List[Dict]:
        """
        Get hands filtered by outcome

        Args:
            outcome: Outcome to filter by ('won', 'lost', 'folded')

        Returns:
            List of matching hand dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM hands
                WHERE outcome = ?
                ORDER BY timestamp DESC
            ''', (outcome,))

            rows = cursor.fetchall()
            conn.close()

            hands = []
            for row in rows:
                hand = dict(row)
                hand['your_cards'] = json.loads(hand['your_cards'])
                hand['board'] = json.loads(hand['board']) if hand['board'] else []
                hand['actions'] = json.loads(hand['actions']) if hand['actions'] else []
                hands.append(hand)

            return hands

        except Exception as e:
            logger.error(f"Error getting hands by outcome: {e}")
            return []

    def get_statistics(self) -> Dict:
        """
        Get overall statistics

        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total hands
            cursor.execute('SELECT COUNT(*) FROM hands')
            total_hands = cursor.fetchone()[0]

            # Hands by outcome
            cursor.execute('''
                SELECT outcome, COUNT(*) as count
                FROM hands
                GROUP BY outcome
            ''')
            outcome_counts = dict(cursor.fetchall())

            # Total profit
            cursor.execute('SELECT SUM(profit) FROM hands')
            total_profit = cursor.fetchone()[0] or 0

            # Average profit per hand
            avg_profit = total_profit / total_hands if total_hands > 0 else 0

            # Win rate
            wins = outcome_counts.get('won', 0)
            win_rate = (wins / total_hands * 100) if total_hands > 0 else 0

            conn.close()

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

    def clear_history(self) -> bool:
        """
        Clear all hand history

        Returns:
            True if cleared successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM hands')
            conn.commit()
            conn.close()

            logger.info("Hand history cleared")
            return True

        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create hand history
    history = HandHistory()

    # Example hand data
    example_hand = {
        'hand_id': 'test_hand_001',
        'your_cards': ['A♠', 'K♥'],
        'board': ['Q♥', 'J♦', '10♣', '9♠', '2♥'],
        'actions': [
            {'player': 0, 'action': 'RAISE', 'amount': 30, 'phase': 'PREFLOP'},
            {'player': 1, 'action': 'CALL', 'amount': 30, 'phase': 'PREFLOP'},
            {'player': 0, 'action': 'BET', 'amount': 50, 'phase': 'FLOP'},
            {'player': 1, 'action': 'CALL', 'amount': 50, 'phase': 'FLOP'},
        ],
        'pot': 150,
        'winner': 0,
        'outcome': 'won',
        'profit': 75,
        'phase': 'RIVER',
        'position': 'Button',
        'notes': 'Good aggressive play with straight'
    }

    # Save hand
    print("💾 Saving example hand...")
    history.save_hand(example_hand)

    # Get statistics
    stats = history.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  • Total hands: {stats['total_hands']}")
    print(f"  • Win rate: {stats['win_rate']}%")
    print(f"  • Total profit: ${stats['total_profit']}")
    print(f"  • Avg profit/hand: ${stats['avg_profit']}")

    # Get recent hands
    recent = history.get_recent_hands(limit=5)
    print(f"\n📋 Recent hands: {len(recent)}")
    for hand in recent:
        print(f"  • {hand['hand_id']}: {hand['outcome']} (${hand['profit']})")
