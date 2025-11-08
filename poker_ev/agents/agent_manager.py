"""
Agent manager for coordinating AI opponents
"""

from texasholdem import TexasHoldEm, ActionType
from texasholdem.agents import random_agent, call_agent
from typing import Tuple, Callable, Dict

# Type alias for agent functions
AgentFunc = Callable[[TexasHoldEm], Tuple[ActionType, int]]


class AgentManager:
    """
    Manage AI agents for poker.ev

    This class coordinates different AI agents and assigns them to players.
    It provides a unified interface for getting AI actions during gameplay.
    """

    def __init__(self):
        """Initialize the agent manager"""
        self.agents: Dict[int, AgentFunc] = {}

    def register_agent(self, player_id: int, agent_func: AgentFunc):
        """
        Register an AI agent for a specific player

        Args:
            player_id: The player ID (0 is typically human)
            agent_func: Function that takes game state and returns (action, amount)
        """
        self.agents[player_id] = agent_func

    def unregister_agent(self, player_id: int):
        """
        Remove an agent from a player

        Args:
            player_id: The player ID to remove agent from
        """
        if player_id in self.agents:
            del self.agents[player_id]

    def has_agent(self, player_id: int) -> bool:
        """
        Check if a player has an assigned agent

        Args:
            player_id: The player ID to check

        Returns:
            True if player has an agent, False otherwise
        """
        return player_id in self.agents

    def get_action(self, game: TexasHoldEm, player_id: int) -> Tuple[ActionType, int]:
        """
        Get action from AI agent for a player

        Args:
            game: The texasholdem game instance
            player_id: The player ID to get action for

        Returns:
            Tuple of (ActionType, amount) representing the agent's decision
        """
        if player_id in self.agents:
            return self.agents[player_id](game)
        else:
            # Default to random agent if no agent assigned
            return self.random_agent(game)

    # ==================== Built-in Agents ====================
    # These are wrappers around texasholdem's built-in agents

    @staticmethod
    def random_agent(game: TexasHoldEm) -> Tuple[ActionType, int]:
        """
        Random agent - makes random valid moves

        Args:
            game: The game instance

        Returns:
            Random valid action
        """
        return random_agent(game)

    @staticmethod
    def call_agent(game: TexasHoldEm) -> Tuple[ActionType, int]:
        """
        Call agent - always calls or checks (never folds or raises)

        Args:
            game: The game instance

        Returns:
            Call or check action
        """
        return call_agent(game)

    @staticmethod
    def aggressive_agent(game: TexasHoldEm) -> Tuple[ActionType, int]:
        """
        Aggressive agent - raises frequently, rarely folds

        Args:
            game: The game instance

        Returns:
            Aggressive action (raise/call)
        """
        import random

        player = game.current_player

        # Get available moves from the engine
        available_moves = game.get_available_moves()

        # 70% chance to raise if possible
        if ActionType.RAISE in available_moves and random.random() < 0.7:
            # Raise between 2x and 3x the pot
            total_pot = sum(pot.amount for pot in game.pots)
            min_raise = game.min_raise()
            max_raise = game.players[player].chips
            raise_amount = min(max_raise, int(total_pot * random.uniform(2.0, 3.0)))
            raise_amount = max(raise_amount, min_raise)
            return ActionType.RAISE, raise_amount

        # Otherwise call/check
        if ActionType.CALL in available_moves:
            return ActionType.CALL, game.chips_to_call(player)
        if ActionType.CHECK in available_moves:
            return ActionType.CHECK, 0

        # Last resort - fold
        return ActionType.FOLD, 0

    @staticmethod
    def tight_agent(game: TexasHoldEm) -> Tuple[ActionType, int]:
        """
        Tight agent - folds often, only plays strong hands

        Args:
            game: The game instance

        Returns:
            Conservative action
        """
        import random

        player = game.current_player

        # Get available moves from the engine
        available_moves = game.get_available_moves()

        # If we can check, always check
        if ActionType.CHECK in available_moves:
            return ActionType.CHECK, 0

        # 60% chance to fold if we have to call
        if ActionType.CALL in available_moves:
            if random.random() < 0.6:
                return ActionType.FOLD, 0
            else:
                return ActionType.CALL, game.chips_to_call(player)

        # Rarely raise (20% chance)
        if ActionType.RAISE in available_moves and random.random() < 0.2:
            min_raise = game.min_raise()
            return ActionType.RAISE, min_raise

        # Default to fold
        return ActionType.FOLD, 0

    def setup_default_agents(self, num_players: int, human_player: int = 0):
        """
        Setup a default mix of AI agents

        Args:
            num_players: Total number of players
            human_player: Which player is human (won't get an agent)
        """
        agents = [
            self.call_agent,
            self.random_agent,
            self.aggressive_agent,
            self.tight_agent,
        ]

        agent_index = 0
        for player_id in range(num_players):
            if player_id == human_player:
                continue  # Skip human player

            # Assign agent in round-robin fashion
            self.register_agent(player_id, agents[agent_index % len(agents)])
            agent_index += 1
