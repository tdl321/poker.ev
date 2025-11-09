"""
Game Context Provider for poker.ev

Converts game state into LLM-friendly context for poker advice.
"""

from texasholdem import Card, HandPhase
from poker_ev.engine.game_wrapper import PokerGame
from typing import Dict, List, Optional


class GameContextProvider:
    """
    Provides formatted game context for LLM poker advisor

    Converts internal game state into natural language descriptions
    that the LLM can understand and analyze.
    """

    # Card suit symbols
    SUIT_SYMBOLS = {
        1: '♠',  # Spades
        2: '♥',  # Hearts
        4: '♦',  # Diamonds
        8: '♣'   # Clubs
    }

    # Rank symbols (0-indexed to match texasholdem library)
    RANK_SYMBOLS = {
        12: 'A', 11: 'K', 10: 'Q', 9: 'J', 8: 'T',
        7: '9', 6: '8', 5: '7', 4: '6', 3: '5',
        2: '4', 1: '3', 0: '2'
    }

    # Position names (for 6-player game)
    POSITION_NAMES_6 = {
        0: "Button (BTN)",
        1: "Small Blind (SB)",
        2: "Big Blind (BB)",
        3: "Under the Gun (UTG)",
        4: "Middle Position (MP)",
        5: "Cutoff (CO)"
    }

    def __init__(self, game: PokerGame):
        """
        Initialize context provider

        Args:
            game: PokerGame instance
        """
        self.game = game

    def card_to_string(self, card: Card) -> str:
        """
        Convert Card object to readable string

        Args:
            card: texasholdem Card object

        Returns:
            String like "A♠" or "K♥"
        """
        rank = self.RANK_SYMBOLS.get(card.rank, str(card.rank))
        suit = self.SUIT_SYMBOLS.get(card.suit, '?')
        return f"{rank}{suit}"

    def cards_to_string(self, cards: List[Card]) -> str:
        """
        Convert list of cards to readable string

        Args:
            cards: List of Card objects

        Returns:
            String like "A♠ K♥" or "Q♦ Q♣"
        """
        return ' '.join(self.card_to_string(card) for card in cards)

    def get_position_name(self, player_id: int, dealer_id: int) -> str:
        """
        Get position name for a player

        Args:
            player_id: Player ID
            dealer_id: Dealer button position

        Returns:
            Position name (e.g., "Button", "Big Blind")
        """
        # Calculate relative position from dealer
        num_players = self.game.num_players
        relative_pos = (player_id - dealer_id) % num_players

        if num_players == 6:
            return self.POSITION_NAMES_6.get(relative_pos, f"Position {relative_pos}")

        # Generic position names for other table sizes
        if relative_pos == 0:
            return "Button (BTN)"
        elif relative_pos == 1:
            return "Small Blind (SB)"
        elif relative_pos == 2:
            return "Big Blind (BB)"
        else:
            return f"Position {relative_pos}"

    def get_hand_phase_name(self, phase: HandPhase) -> str:
        """
        Get readable name for hand phase

        Args:
            phase: HandPhase enum value

        Returns:
            Phase name (e.g., "FLOP", "TURN")
        """
        phase_names = {
            HandPhase.PREFLOP: "PRE-FLOP",
            HandPhase.FLOP: "FLOP",
            HandPhase.TURN: "TURN",
            HandPhase.RIVER: "RIVER",
            HandPhase.SETTLE: "SHOWDOWN"
        }
        return phase_names.get(phase, str(phase))

    def get_current_situation(self) -> str:
        """
        Get current game situation as formatted text

        Returns:
            Multi-line string describing current game state
        """
        state = self.game.get_game_state()

        if not state['hand_active']:
            return "No active hand. Waiting for next hand to start."

        # Get current player info
        current_player_id = state.get('current_player')
        if current_player_id is None or current_player_id != 0:
            return "Waiting for your turn..."

        # Build situation description
        lines = []
        lines.append("=" * 60)
        lines.append("CURRENT HAND")
        lines.append("=" * 60)

        # Your cards
        player = state['players'][0]
        if player.get('hand'):
            cards_str = self.cards_to_string(player['hand'])
            lines.append(f"\n🃏 YOUR CARDS: {cards_str}")

        # Position
        dealer_id = self.game.engine.btn_loc
        position = self.get_position_name(0, dealer_id)
        lines.append(f"📍 POSITION: {position}")

        # Phase and board
        phase_name = self.get_hand_phase_name(state['hand_phase'])
        lines.append(f"\n🎯 PHASE: {phase_name}")

        if state['board']:
            board_str = self.cards_to_string(state['board'])
            lines.append(f"🎴 BOARD: {board_str}")

        # Pot and betting
        lines.append(f"\n💰 POT: ${state['pot']}")
        lines.append(f"💵 YOUR CHIPS: ${player['chips']}")

        chips_to_call = state.get('chips_to_call', 0)
        if chips_to_call > 0:
            lines.append(f"📢 TO CALL: ${chips_to_call}")
        else:
            lines.append(f"📢 TO CALL: $0 (you can check)")

        min_raise = state.get('min_raise', 0)
        if min_raise > 0:
            lines.append(f"📊 MIN RAISE: ${min_raise}")

        # Opponents status
        lines.append(f"\n{'=' * 60}")
        lines.append("OPPONENTS")
        lines.append("=" * 60)

        for i, opp in enumerate(state['players']):
            if i == 0:  # Skip human player
                continue

            if not opp.get('in_game'):
                continue

            status_parts = []

            # Position
            opp_position = self.get_position_name(i, dealer_id)
            status_parts.append(f"Position: {opp_position}")

            # Chips
            status_parts.append(f"${opp['chips']}")

            # Current bet
            if opp.get('bet', 0) > 0:
                status_parts.append(f"BET ${opp['bet']}")

            # Status
            if opp.get('folded'):
                status_parts.append("FOLDED")
            elif opp.get('all_in'):
                status_parts.append("ALL-IN")
            elif opp.get('active'):
                status_parts.append("ACTIVE")

            # Agent type (if available)
            agent_types = {
                1: "Call Agent (always calls)",
                2: "Random Agent (unpredictable)",
                3: "Aggressive Agent (raises often)",
                4: "Tight Agent (folds often)",
                5: "Random Agent (unpredictable)"
            }
            agent_type = agent_types.get(i, "Unknown")

            lines.append(f"\nPlayer {i} ({agent_type}):")
            lines.append(f"  {', '.join(status_parts)}")

        lines.append(f"\n{'=' * 60}")

        return '\n'.join(lines)

    def get_action_summary(self, action_type: str, amount: int = 0) -> str:
        """
        Get summary of an action

        Args:
            action_type: Action type (FOLD, CALL, RAISE, etc.)
            amount: Bet amount if applicable

        Returns:
            Action description string
        """
        if action_type == "FOLD":
            return "You folded"
        elif action_type == "CHECK":
            return "You checked"
        elif action_type == "CALL":
            return f"You called ${amount}"
        elif action_type == "RAISE":
            return f"You raised to ${amount}"
        elif action_type == "ALL_IN":
            return "You went all-in!"
        else:
            return f"You performed action: {action_type}"

    def get_pot_odds(self, chips_to_call: int, pot: int) -> Dict[str, float]:
        """
        Calculate pot odds

        Args:
            chips_to_call: Amount needed to call
            pot: Current pot size

        Returns:
            Dict with pot odds information
        """
        if chips_to_call == 0:
            return {
                'pot_odds_ratio': 0.0,
                'pot_odds_percentage': 0.0,
                'needs_equity': 0.0
            }

        total_pot = pot + chips_to_call
        pot_odds_percentage = (chips_to_call / total_pot) * 100

        return {
            'pot_odds_ratio': total_pot / chips_to_call,
            'pot_odds_percentage': pot_odds_percentage,
            'needs_equity': pot_odds_percentage,  # Equity needed to break even
            'call_amount': chips_to_call,
            'total_pot': total_pot
        }

    def format_pot_odds(self, chips_to_call: int, pot: int) -> str:
        """
        Format pot odds as readable text

        Args:
            chips_to_call: Amount to call
            pot: Current pot

        Returns:
            Formatted pot odds string
        """
        if chips_to_call == 0:
            return "No bet to call (you can check for free)"

        odds = self.get_pot_odds(chips_to_call, pot)

        lines = [
            f"Pot Odds Analysis:",
            f"  • You need to call: ${chips_to_call}",
            f"  • Current pot: ${pot}",
            f"  • Total pot after call: ${odds['total_pot']}",
            f"  • Pot odds: {odds['pot_odds_ratio']:.1f}:1",
            f"  • Break-even equity needed: {odds['needs_equity']:.1f}%"
        ]

        return '\n'.join(lines)

    def get_full_context(self, include_pot_odds: bool = True) -> str:
        """
        Get complete context for LLM including situation and odds

        Args:
            include_pot_odds: Whether to include pot odds calculation

        Returns:
            Complete formatted context string
        """
        situation = self.get_current_situation()

        if not include_pot_odds:
            return situation

        state = self.game.get_game_state()
        if state['hand_active'] and state.get('chips_to_call', 0) > 0:
            pot_odds = self.format_pot_odds(
                state['chips_to_call'],
                state['pot']
            )
            return f"{situation}\n\n{pot_odds}"

        return situation


# Example usage
if __name__ == "__main__":
    from poker_ev.engine.game_wrapper import PokerGame

    # Create a test game
    game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)
    game.start_new_hand()

    # Create context provider
    context = GameContextProvider(game)

    # Display current situation
    print(context.get_full_context())
