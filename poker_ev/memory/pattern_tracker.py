"""
Pattern Tracker for poker.ev

Analyzes player patterns and identifies tendencies using Pinecone semantic search.
"""

from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
import logging

from poker_ev.memory.hand_history import HandHistory
from poker_ev.memory.pinecone_store import PineconeMemoryStore

logger = logging.getLogger(__name__)


class PatternTracker:
    """
    Tracks and analyzes player patterns using Pinecone

    Identifies:
    - Win rate by position
    - Aggression factor
    - Fold frequency
    - Most profitable hand types
    - Common mistakes
    - Opponent tendencies

    Stores patterns as vectors in Pinecone for semantic search.
    """

    def __init__(
        self,
        hand_history: Optional[HandHistory] = None,
        pinecone_store: Optional[PineconeMemoryStore] = None
    ):
        """
        Initialize pattern tracker

        Args:
            hand_history: HandHistory instance (creates new if None)
            pinecone_store: PineconeMemoryStore instance (shares with HandHistory if None)
        """
        if hand_history is None:
            self.hand_history = HandHistory(pinecone_store=pinecone_store)
        else:
            self.hand_history = hand_history

        # Use the same Pinecone store as hand_history
        self.store = self.hand_history.store

    def get_win_rate_by_position(self) -> Dict[str, Dict]:
        """
        Calculate win rate for each position

        Returns:
            Dict mapping position to win rate and hand count
        """
        hands = self.hand_history.get_recent_hands(limit=1000)

        position_stats = defaultdict(lambda: {'wins': 0, 'total': 0})

        for hand in hands:
            position = hand.get('position', 'unknown')
            position_stats[position]['total'] += 1

            if hand.get('outcome') == 'won':
                position_stats[position]['wins'] += 1

        # Calculate win rates
        result = {}
        for position, stats in position_stats.items():
            total = stats['total']
            wins = stats['wins']
            win_rate = (wins / total * 100) if total > 0 else 0

            result[position] = {
                'hands': total,
                'wins': wins,
                'win_rate': round(win_rate, 1)
            }

        return result

    def get_aggression_factor(self) -> Dict[str, float]:
        """
        Calculate aggression factor (raises / calls)

        Returns:
            Dict with aggression metrics
        """
        hands = self.hand_history.get_recent_hands(limit=1000)

        raises = 0
        calls = 0
        bets = 0

        for hand in hands:
            actions = hand.get('actions', [])
            if isinstance(actions, list):
                for action in actions:
                    if isinstance(action, dict) and action.get('player') == 0:  # Only count human player
                        action_type = action.get('action', '').upper()
                        if action_type == 'RAISE':
                            raises += 1
                        elif action_type == 'CALL':
                            calls += 1
                        elif action_type == 'BET':
                            bets += 1

        total_aggressive = raises + bets
        total_passive = calls

        aggression_factor = (
            total_aggressive / total_passive
            if total_passive > 0
            else float('inf')
        )

        return {
            'raises': raises,
            'bets': bets,
            'calls': calls,
            'aggression_factor': round(aggression_factor, 2) if aggression_factor != float('inf') else aggression_factor,
            'style': self._classify_aggression(aggression_factor)
        }

    def _classify_aggression(self, af: float) -> str:
        """Classify aggression level"""
        if af == float('inf'):
            return "Hyper Aggressive"
        elif af < 0.5:
            return "Very Passive"
        elif af < 1.0:
            return "Passive"
        elif af < 2.0:
            return "Balanced"
        elif af < 3.0:
            return "Aggressive"
        else:
            return "Very Aggressive"

    def get_fold_frequency(self) -> Dict[str, float]:
        """
        Calculate fold frequency by phase

        Returns:
            Dict with fold statistics
        """
        hands = self.hand_history.get_recent_hands(limit=1000)

        phase_stats = defaultdict(lambda: {'folds': 0, 'total': 0})

        for hand in hands:
            phase = hand.get('phase', 'unknown')
            phase_stats[phase]['total'] += 1

            if hand.get('outcome') == 'folded':
                phase_stats[phase]['folds'] += 1

        # Calculate fold rates
        result = {}
        for phase, stats in phase_stats.items():
            total = stats['total']
            folds = stats['folds']
            fold_rate = (folds / total * 100) if total > 0 else 0

            result[phase] = {
                'total_hands': total,
                'folds': folds,
                'fold_rate': round(fold_rate, 1)
            }

        return result

    def save_pattern(self, pattern_data: Dict) -> bool:
        """
        Save a discovered pattern to Pinecone

        Args:
            pattern_data: Pattern information
                Required: pattern_id, pattern_name, description
                Optional: category, frequency, win_rate, avg_profit,
                         positions, actions, success, hand_ids, insight

        Returns:
            True if saved successfully
        """
        try:
            if 'timestamp' not in pattern_data:
                pattern_data['timestamp'] = datetime.now().isoformat()

            return self.store.save_pattern(pattern_data)

        except Exception as e:
            logger.error(f"Error saving pattern: {e}")
            return False

    def search_patterns(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for patterns using semantic search

        Args:
            query: Search query (e.g., "aggressive button play")
            limit: Maximum number of patterns to return

        Returns:
            List of matching patterns
        """
        try:
            results = self.store.search_patterns(query=query, top_k=limit)

            patterns = []
            for result in results:
                pattern = result.get('metadata', {})
                pattern['similarity_score'] = result.get('score')
                patterns.append(pattern)

            return patterns

        except Exception as e:
            logger.error(f"Error searching patterns: {e}")
            return []

    def identify_leaks(self) -> List[str]:
        """
        Identify potential leaks in play

        Returns:
            List of leak descriptions
        """
        leaks = []

        # Check win rate by position
        position_stats = self.get_win_rate_by_position()
        for position, stats in position_stats.items():
            if stats['hands'] >= 10:  # Need sufficient sample
                if stats['win_rate'] < 30 and 'Early' in position:
                    leaks.append(
                        f"Low win rate in {position} ({stats['win_rate']}%). "
                        "Consider tightening your opening range from early position."
                    )

        # Check aggression
        aggression = self.get_aggression_factor()
        af = aggression['aggression_factor']
        if af != float('inf') and af < 0.5:
            leaks.append(
                f"Very passive play (AF: {af}). "
                "Consider raising and betting more often for value and to build pots."
            )

        # Check fold frequency
        fold_freq = self.get_fold_frequency()
        for phase, stats in fold_freq.items():
            if stats['total_hands'] >= 10:
                if stats['fold_rate'] > 70:
                    leaks.append(
                        f"Folding too much on {phase} ({stats['fold_rate']}%). "
                        "You might be folding profitable hands."
                    )

        # Check profitability
        overall_stats = self.hand_history.get_statistics()
        if overall_stats.get('total_hands', 0) >= 20:
            if overall_stats.get('avg_profit', 0) < -10:
                leaks.append(
                    f"Losing chips on average (${overall_stats['avg_profit']} per hand). "
                    "Review your hand selection and post-flop play."
                )

        # Save leak patterns to Pinecone
        if leaks and len(leaks) > 0:
            leak_pattern = {
                'pattern_id': f"leaks_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'pattern_name': 'Identified Leaks',
                'description': '. '.join(leaks),
                'category': 'leak_detection',
                'frequency': len(leaks),
                'success': False,
                'insight': f"Found {len(leaks)} potential leaks in play style"
            }
            self.save_pattern(leak_pattern)

        return leaks if leaks else ["No major leaks identified. Keep playing solid poker!"]

    def discover_winning_patterns(self, min_hands: int = 5) -> List[Dict]:
        """
        Automatically discover winning patterns from hand history

        Args:
            min_hands: Minimum hands required for a pattern

        Returns:
            List of winning patterns discovered
        """
        patterns = []

        # Analyze winning hands by position
        position_stats = self.get_win_rate_by_position()
        for position, stats in position_stats.items():
            if stats['hands'] >= min_hands and stats['win_rate'] >= 60:
                # This is a winning pattern
                pattern = {
                    'pattern_id': f"winning_position_{position.lower().replace(' ', '_')}",
                    'pattern_name': f"Profitable {position} Play",
                    'description': f"Playing from {position} with {stats['win_rate']}% win rate",
                    'category': 'position_play',
                    'frequency': stats['hands'],
                    'win_rate': stats['win_rate'],
                    'positions': [position],
                    'success': True,
                    'insight': f"{position} is a very profitable position for you. Continue playing solid ranges."
                }
                patterns.append(pattern)
                self.save_pattern(pattern)

        # Search for specific hand patterns using semantic search
        winning_hands = self.hand_history.get_hands_by_outcome('won', limit=100)

        # Group by common characteristics
        if len(winning_hands) >= min_hands:
            # Analyze aggression in winning hands
            aggressive_wins = [h for h in winning_hands if h.get('aggression_level') == 'aggressive']
            if len(aggressive_wins) >= min_hands:
                pattern = {
                    'pattern_id': 'aggressive_winning',
                    'pattern_name': 'Aggressive Play Wins',
                    'description': f"Winning {len(aggressive_wins)} hands through aggressive play",
                    'category': 'play_style',
                    'frequency': len(aggressive_wins),
                    'win_rate': 100.0,  # These are all wins
                    'success': True,
                    'insight': 'Aggressive play is working well. Continue applying pressure.'
                }
                patterns.append(pattern)
                self.save_pattern(pattern)

        logger.info(f"Discovered {len(patterns)} winning patterns")
        return patterns

    def get_opponent_profile(self, player_id: int) -> Dict:
        """
        Build profile of opponent based on observed play

        Args:
            player_id: Opponent player ID

        Returns:
            Dict with opponent tendencies
        """
        # This is a simplified version
        # In production, you'd track opponent actions across hands

        agent_profiles = {
            1: {
                'name': 'Call Agent',
                'vpip': 95,  # Plays almost every hand
                'pfr': 5,    # Rarely raises
                'aggression': 0.2,
                'tendencies': [
                    'Never folds',
                    'Always calls bets',
                    'Easy to extract value from',
                    "Don't bluff this player"
                ],
                'exploits': [
                    'Value bet relentlessly',
                    'Make big bets with strong hands',
                    'Never bluff'
                ]
            },
            2: {
                'name': 'Random Agent',
                'vpip': 50,
                'pfr': 25,
                'aggression': 1.0,
                'tendencies': [
                    'Unpredictable actions',
                    'Makes random moves',
                    'No clear pattern'
                ],
                'exploits': [
                    'Play solid ABC poker',
                    'Avoid fancy plays',
                    'Stick to fundamentals'
                ]
            },
            3: {
                'name': 'Aggressive Agent',
                'vpip': 45,
                'pfr': 35,
                'aggression': 3.5,
                'tendencies': [
                    'Raises 70% of the time',
                    'Applies constant pressure',
                    'Can be bluffing often'
                ],
                'exploits': [
                    'Call down lighter',
                    'Trap with strong hands',
                    "Don't fight fire with fire",
                    'Let them bluff off chips'
                ]
            },
            4: {
                'name': 'Tight Agent',
                'vpip': 15,
                'pfr': 12,
                'aggression': 0.8,
                'tendencies': [
                    'Folds 60% of the time',
                    'Only plays premium hands',
                    'When they bet, they usually have it'
                ],
                'exploits': [
                    'Steal their blinds constantly',
                    'Fold when they show aggression',
                    "Don't pay them off",
                    'Bluff them more'
                ]
            },
            5: {
                'name': 'Random Agent',
                'vpip': 50,
                'pfr': 25,
                'aggression': 1.0,
                'tendencies': [
                    'Unpredictable actions',
                    'Makes random moves'
                ],
                'exploits': [
                    'Play solid poker',
                    'Value bet strong hands'
                ]
            }
        }

        return agent_profiles.get(player_id, {
            'name': f'Player {player_id}',
            'tendencies': ['Unknown opponent'],
            'exploits': ['Observe and adapt']
        })

    def analyze_patterns(self) -> Dict:
        """
        Comprehensive pattern analysis

        Returns:
            Dict with all pattern analysis
        """
        return {
            'win_rate_by_position': self.get_win_rate_by_position(),
            'aggression': self.get_aggression_factor(),
            'fold_frequency': self.get_fold_frequency(),
            'leaks': self.identify_leaks(),
            'overall_stats': self.hand_history.get_statistics()
        }

    def format_analysis_report(self) -> str:
        """
        Create formatted report of pattern analysis

        Returns:
            Multi-line string report
        """
        analysis = self.analyze_patterns()
        lines = []

        lines.append("=" * 60)
        lines.append("PLAYER PATTERN ANALYSIS")
        lines.append("=" * 60)

        # Overall stats
        stats = analysis['overall_stats']
        if stats.get('total_hands', 0) > 0:
            lines.append(f"\nOverall Statistics:")
            lines.append(f"  Total Hands: {stats['total_hands']}")
            lines.append(f"  Win Rate: {stats.get('win_rate', 0)}%")
            lines.append(f"  Total Profit: ${stats.get('total_profit', 0)}")
            lines.append(f"  Avg Profit/Hand: ${stats.get('avg_profit', 0)}")

        # Aggression
        aggression = analysis['aggression']
        lines.append(f"\nAggression Factor:")
        lines.append(f"  Style: {aggression['style']}")
        af = aggression['aggression_factor']
        if af == float('inf'):
            lines.append(f"  Factor: Infinite (all aggressive actions)")
        else:
            lines.append(f"  Factor: {af}")
        lines.append(f"  Raises: {aggression['raises']}, Calls: {aggression['calls']}")

        # Position stats
        pos_stats = analysis['win_rate_by_position']
        if pos_stats:
            lines.append(f"\nWin Rate by Position:")
            for position, stats in sorted(pos_stats.items()):
                if stats['hands'] > 0:
                    lines.append(
                        f"  {position}: {stats['win_rate']}% "
                        f"({stats['wins']}/{stats['hands']} hands)"
                    )

        # Leaks
        leaks = analysis['leaks']
        lines.append(f"\nIdentified Issues:")
        for i, leak in enumerate(leaks, 1):
            lines.append(f"  {i}. {leak}")

        lines.append(f"\n{'=' * 60}")

        return '\n'.join(lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create pattern tracker
    try:
        tracker = PatternTracker()
        print("✅ Pattern tracker initialized with Pinecone")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        exit(1)

    # Get pattern analysis
    print("\nAnalyzing player patterns...")
    report = tracker.format_analysis_report()
    print(report)

    # Discover winning patterns
    print("\n\nDiscovering winning patterns...")
    patterns = tracker.discover_winning_patterns()
    print(f"Found {len(patterns)} winning patterns:")
    for pattern in patterns:
        print(f"  • {pattern['pattern_name']}: {pattern.get('insight', 'N/A')}")

    # Get opponent profile
    print("\n\nOpponent Profile - Player 3 (Aggressive Agent):")
    profile = tracker.get_opponent_profile(3)
    print(f"Name: {profile['name']}")
    print(f"Style: AF {profile.get('aggression', 'N/A')}")
    print("\nTendencies:")
    for tendency in profile.get('tendencies', []):
        print(f"  • {tendency}")
    print("\nHow to Exploit:")
    for exploit in profile.get('exploits', []):
        print(f"  ✓ {exploit}")
