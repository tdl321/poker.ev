"""
Pattern Tracker for poker.ev

Analyzes player patterns and identifies tendencies.
"""

from typing import Dict, List, Optional
from collections import defaultdict
import logging

from poker_ev.memory.hand_history import HandHistory

logger = logging.getLogger(__name__)


class PatternTracker:
    """
    Tracks and analyzes player patterns over time

    Identifies:
    - Win rate by position
    - Aggression factor
    - Fold frequency
    - Most profitable hand types
    - Common mistakes
    - Opponent tendencies
    """

    def __init__(self, hand_history: HandHistory = None):
        """
        Initialize pattern tracker

        Args:
            hand_history: HandHistory instance (creates new if None)
        """
        self.hand_history = hand_history or HandHistory()

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
            for action in actions:
                if action.get('player') == 0:  # Only count human player
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
            'aggression_factor': round(aggression_factor, 2),
            'style': self._classify_aggression(aggression_factor)
        }

    def _classify_aggression(self, af: float) -> str:
        """Classify aggression level"""
        if af < 0.5:
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
        if aggression['aggression_factor'] < 0.5:
            leaks.append(
                f"Very passive play (AF: {aggression['aggression_factor']}). "
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

        return leaks if leaks else ["No major leaks identified. Keep playing solid poker!"]

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
            lines.append(f"\n📊 Overall Statistics:")
            lines.append(f"  • Total Hands: {stats['total_hands']}")
            lines.append(f"  • Win Rate: {stats.get('win_rate', 0)}%")
            lines.append(f"  • Total Profit: ${stats.get('total_profit', 0)}")
            lines.append(f"  • Avg Profit/Hand: ${stats.get('avg_profit', 0)}")

        # Aggression
        aggression = analysis['aggression']
        lines.append(f"\n⚡ Aggression Factor:")
        lines.append(f"  • Style: {aggression['style']}")
        lines.append(f"  • Factor: {aggression['aggression_factor']}")
        lines.append(f"  • Raises: {aggression['raises']}, Calls: {aggression['calls']}")

        # Position stats
        pos_stats = analysis['win_rate_by_position']
        if pos_stats:
            lines.append(f"\n📍 Win Rate by Position:")
            for position, stats in sorted(pos_stats.items()):
                if stats['hands'] > 0:
                    lines.append(
                        f"  • {position}: {stats['win_rate']}% "
                        f"({stats['wins']}/{stats['hands']} hands)"
                    )

        # Leaks
        leaks = analysis['leaks']
        lines.append(f"\n🔍 Identified Issues:")
        for i, leak in enumerate(leaks, 1):
            lines.append(f"  {i}. {leak}")

        lines.append(f"\n{'=' * 60}")

        return '\n'.join(lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create pattern tracker
    tracker = PatternTracker()

    # Get pattern analysis
    print("📊 Analyzing player patterns...\n")
    report = tracker.format_analysis_report()
    print(report)

    # Get opponent profile
    print("\n\n👤 Opponent Profile - Player 3 (Aggressive Agent):")
    profile = tracker.get_opponent_profile(3)
    print(f"Name: {profile['name']}")
    print(f"Style: AF {profile.get('aggression', 'N/A')}")
    print("\nTendencies:")
    for tendency in profile.get('tendencies', []):
        print(f"  • {tendency}")
    print("\nHow to Exploit:")
    for exploit in profile.get('exploits', []):
        print(f"  ✓ {exploit}")
