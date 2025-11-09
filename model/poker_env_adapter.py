import numpy as np
from pokernew import PokerEnv


class PokerEnvAdapter:
    """
    Adapter for PokerEnv to provide a standard RL interface.

    This wraps the PokerEnv to provide:
    - reset() -> initial states for all players
    - step(actions) -> next_states, rewards, done
    - legal_actions(player_id) -> list of valid actions
    """

    def __init__(self, num_players, endowment, small_blind=10, big_blind=20, ante=0):
        """
        Initialize the poker environment adapter.

        Args:
            num_players: Number of players in the game
            endowment: Starting chips for each player
            small_blind: Small blind amount
            big_blind: Big blind amount
            ante: Ante amount (default 0)
        """
        self.num_players = num_players
        self.endowment = endowment
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.ante = ante

        # Create the poker environment
        self.env = PokerEnv(num_players, endowment, small_blind, big_blind, ante)

        # Track previous money for reward calculation
        self.prev_money = [endowment] * num_players

    def reset(self):
        """
        Reset the environment and deal a new hand.

        Returns:
            states: List of initial state vectors for all players
        """
        # Deal new hand
        self.env.deal(self.num_players)

        # Store initial money for reward calculation
        self.prev_money = self.env.money.copy()

        # Get initial states for all players
        states = [self.env.get_state(i) for i in range(self.num_players)]

        return states

    def step(self, player_id, action, raise_amount=0):
        """
        Execute one player's action in the environment.

        Args:
            player_id: Index of the player taking the action
            action: Action to take (0=fold, 1=check, 2=call, 3=raise)
            raise_amount: Amount to raise if action is raise

        Returns:
            next_state: Next state for the player
            reward: Immediate reward for the player
            done: Whether the game is over
        """
        # Store money before action
        money_before = self.env.money[player_id]

        # Take the action
        self.env.take_action(player_id, action, raise_amount)

        # Get next state
        next_state = self.env.get_state(player_id)

        # Calculate immediate reward (change in money)
        # Note: This is just the immediate change; final rewards come at showdown
        reward = self.env.money[player_id] - money_before

        # Check if game is over
        done = self.env.game_over

        return next_state, reward, done

    def advance_round(self):
        """
        Advance to the next betting round (flop, turn, river).

        Returns:
            states: List of state vectors for all players in the new round
            done: Whether the game should end (only 1 active player)
        """
        if len(self.env.community_cards) < 5 and not self.env.game_over:
            self.env.next_round()

        states = [self.env.get_state(i) for i in range(self.num_players)]
        done = self.env.game_over

        return states, done

    def showdown(self):
        """
        Execute showdown and return final rewards.

        Returns:
            rewards: List of final rewards for all players (change in money from start of hand)
        """
        # Store money before showdown
        money_before_showdown = self.env.money.copy()

        # Execute showdown
        self.env.showdown()

        # Calculate final rewards (change in money from start of hand to end)
        rewards = [
            self.env.money[i] - self.prev_money[i]
            for i in range(self.num_players)
        ]

        return rewards

    def legal_actions(self, player_id):
        """
        Get list of legal actions for a player.

        Args:
            player_id: Player index

        Returns:
            legal_actions: List of legal action indices
        """
        legal = []

        if not self.env.active_players[player_id]:
            return legal

        highest_bet = max(self.env.bets) if any(self.env.bets) else 0
        to_call = highest_bet - self.env.bets[player_id]
        player_money = self.env.money[player_id]

        # Fold is always legal
        legal.append(0)

        # Check is legal if there's nothing to call or player has no money
        if to_call == 0 or player_money == 0:
            legal.append(1)

        # Call is legal if there's something to call and player has money
        if to_call > 0 and player_money > 0:
            legal.append(2)

        # Raise is legal if player has money
        if player_money > 0:
            legal.append(3)

        return legal

    def is_round_done(self):
        """
        Check if the current betting round is complete.

        Returns:
            done: True if betting round is complete
        """
        return self.env.is_round_done()

    def get_active_players(self):
        """
        Get list of active players who can still act.

        Returns:
            active_players: List of player indices who are active and need to act
        """
        active = []
        for i in range(self.num_players):
            if self.env.active_players[i] and not self.env.played[i] and self.env.money[i] > 0:
                active.append(i)
        return active

    def get_phase(self):
        """
        Get the current phase of the game.

        Returns:
            phase: String describing the current phase
        """
        num_community = len(self.env.community_cards)
        if num_community == 0:
            return "Pre-Flop"
        elif num_community == 3:
            return "Flop"
        elif num_community == 4:
            return "Turn"
        elif num_community == 5:
            return "River"
        else:
            return "Unknown"


# Reward transformation functions
def risk_averse_reward(r):
    """
    Risk-averse reward transformation: compresses extreme rewards.

    Uses a logarithmic-like transformation to reduce the impact of large wins/losses.

    Args:
        r: Raw reward

    Returns:
        transformed_reward: Compressed reward
    """
    if r > 0:
        return np.log1p(r)  # log(1 + r) for positive rewards
    elif r < 0:
        return -np.log1p(-r)  # -log(1 - r) for negative rewards
    else:
        return 0


def risk_neutral_reward(r):
    """
    Risk-neutral reward transformation: linear (no transformation).

    Args:
        r: Raw reward

    Returns:
        transformed_reward: Same as input
    """
    return r


def risk_seeking_reward(r):
    """
    Risk-seeking reward transformation: amplifies extreme rewards.

    Uses a quadratic transformation to increase the impact of large wins/losses.

    Args:
        r: Raw reward

    Returns:
        transformed_reward: Amplified reward
    """
    if r > 0:
        return r * r / 100.0  # Square positive rewards (scaled to avoid explosion)
    elif r < 0:
        return -((r * r) / 100.0)  # Square negative rewards
    else:
        return 0
