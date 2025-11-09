"""
State converter for translating between TexasHoldEm and PokerEnv state formats

This module provides utilities to convert game state from the texasholdem library
to the 44-dimensional state vector format used by the trained neural network models.
"""

import numpy as np
from texasholdem import TexasHoldEm, Card, PlayerState
from typing import List


# Maximum number of players supported by PokerEnv
MAX_NUM_PLAYERS = 9


def convert_card_to_tuple(card: Card) -> tuple:
    """
    Convert texasholdem Card object to (rank, suit) tuple format used by PokerEnv.

    Args:
        card: Card object from texasholdem library

    Returns:
        tuple: (rank, suit) where:
            - rank: 2-14 (2-10, J=11, Q=12, K=13, A=14)
            - suit: 1=Spade, 2=Heart, 3=Diamond, 4=Club

    Note:
        texasholdem uses rank 0-12 (0=2, 12=A) and suit 1,2,4,8 (binary flags)
        PokerEnv uses rank 2-14 and suit 1,2,3,4
    """
    # Convert rank: texasholdem 0-12 -> PokerEnv 2-14
    rank = card.rank + 2

    # Convert suit: texasholdem binary flags -> PokerEnv 1,2,3,4
    # texasholdem: 1=spade, 2=heart, 4=diamond, 8=club
    # PokerEnv: 1=spade, 2=heart, 3=diamond, 4=club
    suit_map = {
        1: 1,  # Spade
        2: 2,  # Heart
        4: 3,  # Diamond
        8: 4,  # Club
    }
    suit = suit_map.get(card.suit, 1)

    return (rank, suit)


def texasholdem_to_pokerenv_state(game: TexasHoldEm, player_id: int) -> np.ndarray:
    """
    Convert TexasHoldEm game state to 44-dimensional state vector for neural network.

    Args:
        game: TexasHoldEm game instance
        player_id: ID of the player to generate state for

    Returns:
        np.ndarray: 44-dimensional state vector matching PokerEnv.get_state() format:
            - ranks[0:7]: card ranks (hand + community, padded to 7)
            - suits[7:14]: card suits (hand + community, padded to 7)
            - player_id[14]: current player ID
            - active_players[15:24]: boolean for each player (9 max)
            - pot[24]: total pot
            - current_bet[25]: current bet for this player
            - bets[26:35]: all player bets (9 max)
            - money[35:44]: all player chip stacks (9 max)
    """
    # Get player's hand
    player_hand = game.get_hand(player_id) if game.is_hand_running() else []

    # Get community cards
    community_cards = game.board if game.is_hand_running() else []

    # Convert cards to (rank, suit) tuples
    hand_tuples = [convert_card_to_tuple(card) for card in player_hand]
    community_tuples = [convert_card_to_tuple(card) for card in community_cards]

    # Combine hand and community cards
    all_cards = hand_tuples + community_tuples

    # Extract ranks and suits, pad to 7 cards total
    ranks = [card[0] for card in all_cards] + [0] * (7 - len(all_cards))
    suits = [card[1] for card in all_cards] + [0] * (7 - len(all_cards))

    # Get active players (players who haven't folded)
    num_players = len(game.players)
    active_players = []
    for i in range(num_players):
        player = game.players[i]
        is_active = (player.state != PlayerState.SKIP and
                    player.state != PlayerState.OUT)
        active_players.append(1 if is_active else 0)

    # Pad active_players to MAX_NUM_PLAYERS
    active_players += [0] * (MAX_NUM_PLAYERS - len(active_players))

    # Calculate total pot
    total_pot = sum(pot.amount for pot in game.pots)
    # Add current round bets to pot
    total_pot += sum(game.player_bet_amount(i) for i in range(num_players))

    # Get current bet for this player
    current_bet = game.player_bet_amount(player_id)

    # Get all player bets
    bets = [game.player_bet_amount(i) for i in range(num_players)]
    bets += [0] * (MAX_NUM_PLAYERS - len(bets))

    # Get all player chip stacks
    money = [game.players[i].chips for i in range(num_players)]
    money += [0] * (MAX_NUM_PLAYERS - len(money))

    # Build state vector (44 dimensions total)
    state = (ranks +                    # 7 elements
             suits +                     # 7 elements
             [player_id] +               # 1 element
             active_players +            # 9 elements (MAX_NUM_PLAYERS)
             [total_pot, current_bet] +  # 2 elements
             bets +                      # 9 elements (MAX_NUM_PLAYERS)
             money)                      # 9 elements (MAX_NUM_PLAYERS)

    return np.array(state, dtype=np.float32)


def create_mock_pokerenv_for_legal_actions(game: TexasHoldEm, player_id: int):
    """
    Create a minimal mock PokerEnv-like object for legal action checking.

    The PokerAgent.get_legal_actions() method needs access to:
    - active_players
    - bets
    - money

    Args:
        game: TexasHoldEm game instance
        player_id: Player ID

    Returns:
        Mock object with PokerEnv-compatible attributes
    """
    class MockPokerEnv:
        def __init__(self):
            num_players = len(game.players)

            # Active players
            self.active_players = []
            for i in range(num_players):
                player = game.players[i]
                is_active = (player.state != PlayerState.SKIP and
                           player.state != PlayerState.OUT)
                self.active_players.append(is_active)

            # Player bets
            self.bets = [game.player_bet_amount(i) for i in range(num_players)]

            # Player chip stacks
            self.money = [game.players[i].chips for i in range(num_players)]

            # Pot
            self.pot = sum(pot.amount for pot in game.pots)
            self.pot += sum(game.player_bet_amount(i) for i in range(num_players))

    return MockPokerEnv()
