"""
Game engine wrapper for texasholdem

This module provides a GUI-friendly interface to texasholdem's TexasHoldEm class.
"""

from texasholdem import TexasHoldEm, Card, ActionType, HandPhase, PlayerState
from typing import List, Dict, Optional, Tuple


class PokerGame:
    """
    Wrapper around texasholdem.TexasHoldEm with GUI-friendly interface

    This class provides a simplified API for the GUI to interact with the game engine,
    handling state queries and action execution.
    """

    def __init__(self, num_players: int = 6, buyin: int = 1000,
                 big_blind: int = 10, small_blind: int = 5):
        """
        Initialize a new poker game

        Args:
            num_players: Number of players at the table (2-9)
            buyin: Starting chips for each player
            big_blind: Big blind amount
            small_blind: Small blind amount
        """
        self.num_players = num_players
        self.buyin = buyin
        self.big_blind = big_blind
        self.small_blind = small_blind

        self.engine = TexasHoldEm(
            buyin=buyin,
            big_blind=big_blind,
            small_blind=small_blind,
            max_players=num_players
        )

    def start_new_hand(self) -> bool:
        """
        Start a new hand

        Returns:
            True if hand started successfully, False otherwise
        """
        try:
            self.engine.start_hand()
            return True
        except Exception as e:
            print(f"Error starting hand: {e}")
            return False

    def get_game_state(self) -> Dict:
        """
        Get complete game state for rendering

        Returns:
            Dictionary containing all relevant game state information
        """
        if not self.engine.is_hand_running():
            return {
                'hand_active': False,
                'current_player': None,
                'hand_phase': None,
                'board': [],
                'pot': 0,
                'players': self._get_player_states(),
                'valid_actions': [],
                'chips_to_call': 0,
            }

        current = self.engine.current_player

        # Calculate total pot from all pots plus player bets
        total_pot = sum(pot.amount for pot in self.engine.pots)
        # Add all current player bets (blinds and current round bets)
        total_pot += sum(self.engine.player_bet_amount(i) for i in range(len(self.engine.players)))

        return {
            'hand_active': True,
            'current_player': current,
            'hand_phase': self.engine.hand_phase,
            'board': self.engine.board,
            'pot': total_pot,
            'players': self._get_player_states(),
            'valid_actions': self._get_valid_actions(),
            'chips_to_call': self.engine.chips_to_call(current) if current is not None else 0,
            'min_raise': self._get_min_raise(),
        }

    def _get_player_states(self) -> List[Dict]:
        """
        Get state for all players

        Returns:
            List of player state dictionaries
        """
        states = []

        for player_id in range(self.num_players):
            # Check if player is still in the game
            if player_id >= len(self.engine.players):
                states.append({'active': False, 'in_game': False})
                continue

            player = self.engine.players[player_id]

            # Check if player is in current hand (not folded or out)
            is_active = player.state != PlayerState.SKIP and player.state != PlayerState.OUT
            is_folded = player.state == PlayerState.SKIP

            if not is_active:
                states.append({
                    'active': False,
                    'in_game': True,
                    'id': player_id,
                    'chips': player.chips,
                })
                continue

            states.append({
                'active': True,
                'in_game': True,
                'id': player_id,
                'chips': player.chips,
                'bet': self.engine.player_bet_amount(player_id),
                'hand': self.engine.get_hand(player_id) if self.engine.is_hand_running() else [],
                'folded': is_folded,
                'all_in': player.state == PlayerState.ALL_IN,
            })

        return states

    def _get_valid_actions(self) -> List[ActionType]:
        """
        Get valid actions for current player

        Returns:
            List of valid ActionType values
        """
        if not self.engine.is_hand_running():
            return []

        player = self.engine.current_player
        if player is None:
            return []

        # Get available moves from the engine
        available_moves = self.engine.get_available_moves()

        # Extract unique action types from available moves
        actions = []
        for action_type in [ActionType.FOLD, ActionType.CHECK, ActionType.CALL,
                           ActionType.RAISE, ActionType.ALL_IN]:
            if action_type in available_moves:
                actions.append(action_type)

        return actions

    def _get_min_raise(self) -> int:
        """
        Get minimum raise amount

        Returns:
            Minimum valid raise amount
        """
        if not self.engine.is_hand_running():
            return 0

        player = self.engine.current_player
        if player is None:
            return 0

        # Use the engine's min_raise method
        return self.engine.min_raise()

    def take_action(self, action: ActionType, amount: int = 0) -> bool:
        """
        Execute a player action

        Args:
            action: The action to take
            amount: Amount for raise (optional)

        Returns:
            True if action was successful, False otherwise
        """
        try:
            if action == ActionType.RAISE:
                self.engine.take_action(action, total=amount)
            else:
                self.engine.take_action(action)
            return True
        except Exception as e:
            print(f"Error taking action {action}: {e}")
            return False

    def is_hand_running(self) -> bool:
        """Check if current hand is still active"""
        return self.engine.is_hand_running()

    def is_game_running(self) -> bool:
        """Check if game is still active (at least 2 players)"""
        return self.engine.is_game_running()

    def is_player_busted(self) -> bool:
        """Check if player 0 (human) has run out of chips"""
        if len(self.engine.players) == 0:
            return True
        return self.engine.players[0].chips <= 0

    def get_hand_history(self) -> str:
        """
        Get the current hand history

        Returns:
            Hand history as a string
        """
        try:
            return str(self.engine.hand_history)
        except:
            return ""

    def export_history(self, filepath: str) -> bool:
        """
        Export game history to PGN file

        Args:
            filepath: Path to save history file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.engine.export_history(filepath)
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False
