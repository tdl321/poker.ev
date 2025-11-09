"""
Agent manager for coordinating AI opponents
"""

from texasholdem import TexasHoldEm, ActionType
from texasholdem.agents import random_agent, call_agent
from typing import Tuple, Callable, Dict, Optional
import random
from pathlib import Path

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

    def register_neural_agent(self, player_id: int, model_path: str,
                              risk_profile: str = 'neutral', verbose: bool = False):
        """
        Register a neural network agent for a specific player.

        Args:
            player_id: The player ID to assign the neural agent to
            model_path: Path to the trained model .pt file
            risk_profile: Risk profile ('neutral', 'averse', 'seeking')
            verbose: If True, log each neural network decision
        """
        try:
            from poker_ev.agents.neural_agent import create_neural_agent

            # Create neural agent adapter
            neural_agent = create_neural_agent(
                model_path=model_path,
                player_id=player_id,
                risk_profile=risk_profile,
                verbose=verbose
            )

            # Register with agent manager
            self.register_agent(player_id, neural_agent)

        except ImportError as e:
            print(f"⚠ Warning: Could not load neural agent: {e}")
            print(f"   Falling back to random agent for player {player_id}")
            self.register_agent(player_id, self.random_agent)

    def setup_neural_agents(self, num_players: int, human_player: int = 0,
                           model_dir: Optional[str] = None, verbose: bool = False):
        """
        Setup neural network agents with random mix of risk profiles.

        Creates 5 AI agents with random distribution of:
        - Risk-seeking (aggressive)
        - Risk-averse (conservative)
        - Risk-neutral (balanced)

        Args:
            num_players: Total number of players (should be 6: 1 human + 5 AI)
            human_player: Which player is human (default: 0)
            model_dir: Directory containing trained model files (default: model/)
            verbose: If True, log each neural network decision (useful for debugging)
        """
        if model_dir is None:
            # Default to model/ directory in project root
            project_root = Path(__file__).parent.parent.parent
            model_dir = project_root / "model"
        else:
            model_dir = Path(model_dir)

        # Risk profiles with their model file patterns
        risk_profiles = ['neutral', 'averse', 'seeking']

        # Generate random mix of 5 agents from 3 risk profiles
        # This will create a random combination that adds up to 5 agents
        ai_player_count = num_players - 1  # Exclude human player
        ai_risk_profiles = random.choices(risk_profiles, k=ai_player_count)

        print(f"\n🎲 Setting up {ai_player_count} neural agents with random risk profiles:")
        print(f"   Distribution: {dict(zip(*list(zip(*[(p, ai_risk_profiles.count(p)) for p in set(ai_risk_profiles)]))))}")

        # Assign agents to players
        agent_index = 0
        for player_id in range(num_players):
            if player_id == human_player:
                continue  # Skip human player

            risk_profile = ai_risk_profiles[agent_index]

            # Look for trained model file
            # Pattern: poker_agent_{id}_{risk_profile}.pt
            # Try to find any model with this risk profile
            model_files = list(model_dir.glob(f"poker_agent_*_{risk_profile}.pt"))

            if model_files:
                # Use the first matching model file
                model_path = str(model_files[0])
                print(f"   Player {player_id}: {risk_profile:8s} <- {model_files[0].name}")
            else:
                # Fallback: use untrained model (will warn in neural_agent.py)
                model_path = str(model_dir / f"poker_agent_0_{risk_profile}.pt")
                print(f"   Player {player_id}: {risk_profile:8s} (untrained)")

            # Register neural agent
            self.register_neural_agent(
                player_id=player_id,
                model_path=model_path,
                risk_profile=risk_profile,
                verbose=verbose
            )

            agent_index += 1

        if verbose:
            print(f"\n💡 Verbose mode enabled - neural network decisions will be logged during gameplay")

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
