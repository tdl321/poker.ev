"""
Neural network agent adapter for poker.ev GUI

This module provides an adapter that wraps trained PokerAgent models to work
with the AgentManager interface in the poker.ev GUI.
"""

import sys
from pathlib import Path
import torch
from texasholdem import TexasHoldEm, ActionType
from typing import Tuple

# Add model directory to path to import PokerAgent
model_dir = Path(__file__).parent.parent.parent / "model"
sys.path.insert(0, str(model_dir))

from poker_agent import PokerAgent
from poker_ev.agents.state_converter import (
    texasholdem_to_pokerenv_state,
    create_mock_pokerenv_for_legal_actions
)


class NeuralAgentAdapter:
    """
    Adapter that wraps a trained PokerAgent to work with AgentManager.

    This class bridges the gap between the trained neural network models
    (which expect PokerEnv state format) and the GUI's game engine
    (which uses TexasHoldEm library).
    """

    # Map PokerEnv action indices to TexasHoldEm ActionType
    ACTION_MAP = {
        0: ActionType.FOLD,
        1: ActionType.CHECK,
        2: ActionType.CALL,
        3: ActionType.RAISE,
    }

    def __init__(self, model_path: str, player_id: int, risk_profile: str = 'neutral', verbose: bool = False):
        """
        Initialize the neural agent adapter.

        Args:
            model_path: Path to trained model .pt file
            player_id: ID of the player this agent controls
            risk_profile: Risk profile of the agent ('neutral', 'averse', 'seeking')
            verbose: If True, print decision-making details
        """
        self.player_id = player_id
        self.risk_profile = risk_profile
        self.verbose = verbose
        self.decision_count = 0

        # State dimension must match training (44 from PokerEnv.get_state)
        state_dim = 44
        hidden_dim = 128

        # Create and load the trained model
        self.model = PokerAgent(
            state_dim=state_dim,
            hidden_dim=hidden_dim,
            risk_profile=risk_profile,
            device='cpu'  # Use CPU for GUI (faster for single inference)
        )

        # Load trained weights
        self.weights_loaded = False
        try:
            self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
            self.model.eval()  # Set to evaluation mode
            self.weights_loaded = True
            print(f"✓ Loaded neural agent: {model_path} (risk_profile={risk_profile})")
        except FileNotFoundError:
            print(f"⚠ Warning: Model file not found: {model_path}")
            print(f"   Neural agent will use untrained weights for player {player_id}")
        except Exception as e:
            print(f"⚠ Warning: Error loading model {model_path}: {e}")
            print(f"   Neural agent will use untrained weights for player {player_id}")

    def __call__(self, game: TexasHoldEm) -> Tuple[ActionType, int]:
        """
        Get action from the neural agent for the current game state.

        This method is called by AgentManager and must return (ActionType, amount).

        Args:
            game: TexasHoldEm game instance

        Returns:
            Tuple[ActionType, int]: (action, amount) where:
                - action: ActionType enum value
                - amount: Raise amount (0 if not raising)
        """
        # Convert game state to PokerEnv format (44-dim vector)
        state = texasholdem_to_pokerenv_state(game, self.player_id)

        # Create mock PokerEnv for legal action checking
        mock_env = create_mock_pokerenv_for_legal_actions(game, self.player_id)

        # Get action from model
        with torch.no_grad():
            action_idx, raise_amount, _, _ = self.model.act(
                state=state,
                env=mock_env,
                player_id=self.player_id
            )

        # Track decision count
        self.decision_count += 1

        # Convert PokerEnv action index to TexasHoldEm ActionType
        action = self.ACTION_MAP[action_idx]

        # Log neural network decision if verbose
        if self.verbose:
            print(f"[NN Player {self.player_id} ({self.risk_profile})]: Decision #{self.decision_count} → {action.name}")

        # Handle raise action
        if action == ActionType.RAISE:
            # Defensive check: if raise amount is invalid, fall back to CALL/CHECK
            if raise_amount is None or raise_amount <= 0:
                # Get available actions from the game
                available_actions = game.get_available_moves()

                # Try to fall back to CALL if available, otherwise CHECK
                if ActionType.CALL in available_actions:
                    action = ActionType.CALL
                    amount = 0
                elif ActionType.CHECK in available_actions:
                    action = ActionType.CHECK
                    amount = 0
                else:
                    # Last resort: FOLD (should not happen, but prevents infinite loop)
                    action = ActionType.FOLD
                    amount = 0

                print(f"⚠ Warning: Neural agent selected RAISE with invalid amount {raise_amount}, "
                      f"falling back to {action}")
            else:
                # Convert raise_amount to total bet amount for TexasHoldEm
                # The model outputs a raise amount (how much to add on top of calling)
                # but TexasHoldEm expects total (the total bet amount to raise TO)
                highest_bet = max(game.player_bet_amount(i) for i in range(len(game.players)))
                total_bet_amount = highest_bet + raise_amount

                # Ensure total bet amount is valid
                player_chips = game.players[self.player_id].chips
                current_bet = game.player_bet_amount(self.player_id)
                max_total_possible = current_bet + player_chips

                # Clip to player's available chips
                total_bet_amount = min(total_bet_amount, max_total_possible)

                # Get minimum raise requirement from the game
                min_raise = game.min_raise()
                min_total_required = highest_bet + min_raise

                # Check if total bet meets minimum raise requirement
                if total_bet_amount < min_total_required:
                    # Try to meet minimum raise if we have enough chips
                    if max_total_possible >= min_total_required:
                        # Adjust to meet minimum raise
                        total_bet_amount = min_total_required
                    else:
                        # Can't meet minimum raise, fall back to CALL/CHECK
                        available_actions = game.get_available_moves()
                        if ActionType.CALL in available_actions:
                            action = ActionType.CALL
                            amount = 0
                        elif ActionType.CHECK in available_actions:
                            action = ActionType.CHECK
                            amount = 0
                        else:
                            action = ActionType.FOLD
                            amount = 0
                        print(f"⚠ Warning: Neural agent cannot meet min_raise={min_raise} "
                              f"(has {max_total_possible - highest_bet} available), "
                              f"falling back to {action}")
                        return action, amount

                # Final validation: ensure we're actually raising
                if total_bet_amount <= highest_bet:
                    # Can't raise, fall back to CALL/CHECK
                    available_actions = game.get_available_moves()
                    if ActionType.CALL in available_actions:
                        action = ActionType.CALL
                        amount = 0
                    elif ActionType.CHECK in available_actions:
                        action = ActionType.CHECK
                        amount = 0
                    else:
                        action = ActionType.FOLD
                        amount = 0
                    print(f"⚠ Warning: Neural agent RAISE amount too small (total={total_bet_amount}, "
                          f"highest={highest_bet}), falling back to {action}")
                else:
                    amount = total_bet_amount
        else:
            amount = 0

        return action, amount


def create_neural_agent(model_path: str, player_id: int, risk_profile: str = 'neutral', verbose: bool = False):
    """
    Factory function to create a neural agent adapter.

    Args:
        model_path: Path to trained model .pt file
        player_id: ID of the player this agent controls
        risk_profile: Risk profile ('neutral', 'averse', 'seeking')
        verbose: If True, log each neural network decision

    Returns:
        Callable: Function that takes TexasHoldEm and returns (ActionType, amount)
    """
    adapter = NeuralAgentAdapter(model_path, player_id, risk_profile, verbose)
    return adapter
