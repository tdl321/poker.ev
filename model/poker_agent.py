"""
PyTorch Neural Network Agent for Poker

This module implements a policy network for multi-agent poker reinforcement learning
using best practices from PyTorch documentation and conventions.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class PokerAgent(nn.Module):
    """
    Neural network agent for playing poker with policy gradient learning.

    Architecture:
        Input (state_dim) → FC1 (hidden_dim) → ReLU →
        FC2 (hidden_dim) → ReLU → {Action Head, Raise Head, Value Head}

    Outputs:
        - Action logits: 4 actions (fold, check, call, raise)
        - Raise amount logits: 4 size buckets (small, medium, large, all-in)
        - State value estimate: Scalar value for baseline/critic

    The network uses proper weight initialization (Xavier for linear layers)
    and supports device placement for GPU acceleration.
    """

    def __init__(self, state_dim, hidden_dim=128, risk_profile='neutral', device=None):
        """
        Initialize the poker agent neural network.

        Args:
            state_dim (int): Dimension of the state vector
            hidden_dim (int): Size of hidden layers (default: 128)
            risk_profile (str): One of 'averse', 'neutral', 'seeking' (default: 'neutral')
            device (str or torch.device, optional): Device to place the module on
                                                     (e.g., 'cuda', 'cpu')

        Note:
            Parameters are registered automatically when assigned as attributes.
            Weight initialization uses Xavier normal for better gradient flow.
        """
        super().__init__()

        # Store configuration
        self.state_dim = state_dim
        self.hidden_dim = hidden_dim
        self.risk_profile = risk_profile

        # Determine device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        # Shared feature extractor layers
        # Using separate layers instead of Sequential for flexibility
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)

        # Multi-head outputs
        self.action_head = nn.Linear(hidden_dim, 4)  # 4 poker actions
        self.raise_amount_head = nn.Linear(hidden_dim, 4)  # 4 raise size buckets
        self.value_head = nn.Linear(hidden_dim, 1)  # State value for baseline

        # Initialize weights using Xavier (Glorot) initialization
        # This helps with gradient flow in deep networks
        self._initialize_weights()

        # Move to target device
        self.to(self.device)

    @torch.no_grad()
    def _initialize_weights(self):
        """
        Initialize network weights using Xavier normal initialization.

        Xavier initialization maintains variance of activations and gradients
        across layers, which is beneficial for training stability.

        Reference:
            Glorot & Bengio (2010): Understanding the difficulty of training
            deep feedforward neural networks
        """
        for module in self.modules():
            if isinstance(module, nn.Linear):
                # Xavier normal initialization for weights
                nn.init.xavier_normal_(module.weight)
                # Initialize biases to small positive values
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0.01)

    def forward(self, state):
        """
        Forward pass through the network.

        Args:
            state (torch.Tensor or np.ndarray): State vector
                - Shape: (state_dim,) or (batch_size, state_dim)
                - Automatically handles both single states and batches

        Returns:
            tuple: (action_logits, raise_logits, value)
                - action_logits (torch.Tensor): Shape (batch_size, 4)
                - raise_logits (torch.Tensor): Shape (batch_size, 4)
                - value (torch.Tensor): Shape (batch_size, 1)

        Note:
            The forward method is called implicitly when you call the module
            instance: output = model(input)
        """
        # Convert numpy arrays to tensors if needed
        if isinstance(state, np.ndarray):
            state = torch.from_numpy(state).float()

        # Ensure tensor is on the correct device
        if state.device != self.device:
            state = state.to(self.device)

        # Add batch dimension if input is a single state
        if state.dim() == 1:
            state = state.unsqueeze(0)

        # Shared feature extraction with ReLU activations
        # Using F.relu instead of nn.ReLU() for efficiency (no extra module)
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))

        # Multi-head outputs
        action_logits = self.action_head(x)
        raise_logits = self.raise_amount_head(x)
        value = self.value_head(x)

        return action_logits, raise_logits, value

    def get_legal_actions(self, env, player_id):
        """
        Determine which actions are legal for the current player.

        Args:
            env: PokerEnv instance containing game state
            player_id (int): Index of the player

        Returns:
            torch.Tensor: Boolean mask of shape (4,) where True indicates
                         a legal action. Indices: [0=fold, 1=check, 2=call, 3=raise]

        Note:
            This method encapsulates poker rules for legal actions:
            - Fold is always legal
            - Check is legal when no bet is owed or player is all-in
            - Call is legal when a bet must be matched
            - Raise is legal when player has chips to raise above the current bet
        """
        # Initialize mask on the same device as the model
        legal_mask = torch.zeros(4, dtype=torch.bool, device=self.device)

        # If player is not active, no actions are legal
        if not env.active_players[player_id]:
            return legal_mask

        # Compute betting context
        highest_bet = max(env.bets) if any(env.bets) else 0
        to_call = highest_bet - env.bets[player_id]
        player_money = env.money[player_id]

        # Apply poker rules for legal actions
        legal_mask[0] = True  # Fold is always legal

        # Check is legal if nothing to call or player is all-in
        if to_call == 0 or player_money == 0:
            legal_mask[1] = True

        # Call is legal if there's a bet to match and player has chips
        if to_call > 0 and player_money > 0:
            legal_mask[2] = True

        # Raise is legal only if player has chips remaining AFTER calling
        # (i.e., enough chips to actually raise above the current bet)
        max_raise_possible = max(player_money - to_call, 0)
        if max_raise_possible > 0:
            legal_mask[3] = True

        return legal_mask

    def get_raise_amount(self, env, player_id, raise_bucket_logits):
        """
        Convert raise bucket logits to actual raise amount.

        Args:
            env: PokerEnv instance
            player_id (int): Player index
            raise_bucket_logits (torch.Tensor): Logits for raise size buckets

        Returns:
            int: Raise amount in chips

        Raise Buckets:
            0: Small (25% pot or min 10 chips)
            1: Medium (50% pot or min 20 chips)
            2: Large (75% pot or min 30 chips)
            3: All-in (pot size or all remaining chips)
        """
        # Sample from categorical distribution over raise sizes
        raise_probs = F.softmax(raise_bucket_logits, dim=-1)
        raise_bucket = torch.multinomial(raise_probs, 1).item()

        # Compute betting context
        highest_bet = max(env.bets) if any(env.bets) else 0
        to_call = highest_bet - env.bets[player_id]
        max_raise_possible = max(env.money[player_id] - to_call, 0)
        pot = env.pot

        if max_raise_possible == 0:
            return 0

        # Map bucket to actual raise amount
        # Using pot-relative sizing (common in poker)
        if raise_bucket == 0:
            raise_amount = max(int(0.25 * pot), 10)
        elif raise_bucket == 1:
            raise_amount = max(int(0.50 * pot), 20)
        elif raise_bucket == 2:
            raise_amount = max(int(0.75 * pot), 30)
        else:  # bucket 3
            raise_amount = max(int(pot), max_raise_possible)

        # Clip to available chips
        raise_amount = min(raise_amount, max_raise_possible)

        # Ensure minimum raise if possible
        if raise_amount == 0 and max_raise_possible > 0:
            raise_amount = min(10, max_raise_possible)

        return raise_amount

    def act(self, state, env, player_id):
        """
        Select an action based on the current state (inference mode).

        This method performs action selection without gradient tracking,
        suitable for environment interaction during data collection.

        Args:
            state: State vector from env.get_state(player_id)
            env: PokerEnv instance
            player_id (int): Player index

        Returns:
            tuple: (action, raise_amount, action_logits, value)
                - action (int): Selected action index
                - raise_amount (int): Chips to raise (0 if not raising)
                - action_logits (torch.Tensor): Logits before masking
                - value (float): Estimated state value

        Note:
            Uses torch.no_grad() to disable gradient computation for efficiency
            during inference. Illegal actions are masked out before sampling.
        """
        # Disable gradient computation for inference
        with torch.no_grad():
            # Forward pass
            action_logits, raise_logits, value = self.forward(state)

            # Remove batch dimension for single-state input
            action_logits = action_logits.squeeze(0)
            raise_logits = raise_logits.squeeze(0)
            value = value.item()

        # Get legal actions mask
        legal_mask = self.get_legal_actions(env, player_id)

        # Safety check: if no legal actions available, default to fold
        if not legal_mask.any():
            print(f"WARNING: No legal actions for player {player_id}. Defaulting to fold.")
            print(f"  Active: {env.active_players[player_id]}, Money: {env.money[player_id]}, Bets: {env.bets}")
            action = 0  # Fold
            raise_amount = 0
            return action, raise_amount, action_logits, value

        # Mask illegal actions by setting logits to -inf
        # This ensures zero probability after softmax
        masked_logits = action_logits.clone()
        masked_logits[~legal_mask] = float('-inf')

        # Sample action from categorical distribution over legal actions
        action_probs = F.softmax(masked_logits, dim=-1)

        # Additional safety: check for NaN or Inf in probabilities
        if torch.isnan(action_probs).any() or torch.isinf(action_probs).any():
            print(f"WARNING: Invalid probabilities detected. Logits: {masked_logits}, Probs: {action_probs}")
            # Default to fold
            action = 0
            raise_amount = 0
            return action, raise_amount, action_logits, value

        action = torch.multinomial(action_probs, 1).item()

        # Determine raise amount if raise action was selected
        raise_amount = 0
        if action == 3:  # Raise action
            raise_amount = self.get_raise_amount(env, player_id, raise_logits)

        return action, raise_amount, action_logits, value

    def extra_repr(self):
        """
        Provide extra representation string for module printing.

        This method is called when printing the module to provide additional
        context about the module's configuration.

        Returns:
            str: Extra information about this module

        Example:
            >>> agent = PokerAgent(44, 128, 'neutral')
            >>> print(agent)
            PokerAgent(
              state_dim=44, hidden_dim=128, risk_profile=neutral, device=cpu
              ...
            )
        """
        return (f'state_dim={self.state_dim}, hidden_dim={self.hidden_dim}, '
                f'risk_profile={self.risk_profile}, device={self.device}')
