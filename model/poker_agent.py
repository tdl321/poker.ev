import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class PokerAgent(nn.Module):
    """
    Neural network agent for playing poker.

    Architecture:
    - Input: state vector from PokerEnv.get_state()
    - Hidden layers: fully connected
    - Outputs:
        - Action logits (4 actions: fold, check, call, raise)
        - Raise amount logits (4 buckets: small, medium, large, all-in)
        - State value estimate (scalar)
    """

    def __init__(self, state_dim, hidden_dim=128, risk_profile='neutral'):
        """
        Initialize the poker agent.

        Args:
            state_dim: Dimension of the state vector
            hidden_dim: Size of hidden layers
            risk_profile: One of 'averse', 'neutral', 'seeking'
        """
        super(PokerAgent, self).__init__()

        self.state_dim = state_dim
        self.hidden_dim = hidden_dim
        self.risk_profile = risk_profile

        # Shared feature extractor
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)

        # Action head (fold, check, call, raise)
        self.action_head = nn.Linear(hidden_dim, 4)

        # Raise amount head (4 buckets: 25%, 50%, 75%, 100% of pot or remaining chips)
        self.raise_amount_head = nn.Linear(hidden_dim, 4)

        # Value head (state value estimate)
        self.value_head = nn.Linear(hidden_dim, 1)

    def forward(self, state):
        """
        Forward pass through the network.

        Args:
            state: State vector (batch_size, state_dim) or (state_dim,)

        Returns:
            action_logits: Logits for each action (batch_size, 4)
            raise_logits: Logits for raise amounts (batch_size, 4)
            value: State value estimate (batch_size, 1)
        """
        # Ensure state is a tensor
        if isinstance(state, np.ndarray):
            state = torch.FloatTensor(state)

        # Add batch dimension if needed
        if len(state.shape) == 1:
            state = state.unsqueeze(0)

        # Shared layers
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))

        # Output heads
        action_logits = self.action_head(x)
        raise_logits = self.raise_amount_head(x)
        value = self.value_head(x)

        return action_logits, raise_logits, value

    def get_legal_actions(self, env, player_id):
        """
        Determine which actions are legal for the current player.

        Args:
            env: PokerEnv instance
            player_id: Player index

        Returns:
            legal_mask: Boolean tensor of shape (4,) indicating legal actions
        """
        legal_mask = torch.zeros(4, dtype=torch.bool)

        # If player is not active, no actions are legal
        if not env.active_players[player_id]:
            return legal_mask

        highest_bet = max(env.bets) if any(env.bets) else 0
        to_call = highest_bet - env.bets[player_id]
        player_money = env.money[player_id]

        # Fold is always legal (action 0)
        legal_mask[0] = True

        # Check is legal if there's nothing to call or player has no money (action 1)
        if to_call == 0 or player_money == 0:
            legal_mask[1] = True

        # Call is legal if there's something to call and player has money (action 2)
        if to_call > 0 and player_money > 0:
            legal_mask[2] = True

        # Raise is legal if player has money (action 3)
        if player_money > 0:
            legal_mask[3] = True

        return legal_mask

    def get_raise_amount(self, env, player_id, raise_bucket_logits):
        """
        Convert raise bucket to actual raise amount.

        Args:
            env: PokerEnv instance
            player_id: Player index
            raise_bucket_logits: Logits for raise amount buckets

        Returns:
            raise_amount: Integer raise amount
        """
        # Sample from raise bucket distribution
        raise_probs = F.softmax(raise_bucket_logits, dim=-1)
        raise_bucket = torch.multinomial(raise_probs, 1).item()

        # Calculate raise amount based on bucket
        highest_bet = max(env.bets) if any(env.bets) else 0
        to_call = highest_bet - env.bets[player_id]
        max_raise_possible = max(env.money[player_id] - to_call, 0)
        pot = env.pot

        if max_raise_possible == 0:
            return 0

        # Define raise buckets as percentages of pot or remaining chips
        if raise_bucket == 0:  # Small raise: 25% of pot or 10 chips, whichever is larger
            raise_amount = max(int(0.25 * pot), 10)
        elif raise_bucket == 1:  # Medium raise: 50% of pot
            raise_amount = max(int(0.50 * pot), 20)
        elif raise_bucket == 2:  # Large raise: 75% of pot
            raise_amount = max(int(0.75 * pot), 30)
        else:  # All-in or pot-sized raise
            raise_amount = max(int(pot), max_raise_possible)

        # Clip to available money
        raise_amount = min(raise_amount, max_raise_possible)

        # Ensure raise amount is at least 1 if player chose to raise
        if raise_amount == 0 and max_raise_possible > 0:
            raise_amount = min(10, max_raise_possible)

        return raise_amount

    def act(self, state, env, player_id):
        """
        Select an action based on the current state.

        Args:
            state: State vector from env.get_state(player_id)
            env: PokerEnv instance
            player_id: Player index

        Returns:
            action: Selected action (0=fold, 1=check, 2=call, 3=raise)
            raise_amount: Raise amount if action is raise, else 0
            action_logits: Logits used for action selection
            value: State value estimate
        """
        # Forward pass
        with torch.no_grad():
            action_logits, raise_logits, value = self.forward(state)
            action_logits = action_logits.squeeze(0)  # Remove batch dimension
            raise_logits = raise_logits.squeeze(0)
            value = value.item()

        # Get legal actions
        legal_mask = self.get_legal_actions(env, player_id)

        # Mask illegal actions by setting their logits to -inf
        masked_logits = action_logits.clone()
        masked_logits[~legal_mask] = float('-inf')

        # Sample action from legal actions
        action_probs = F.softmax(masked_logits, dim=-1)
        action = torch.multinomial(action_probs, 1).item()

        # Determine raise amount if action is raise
        raise_amount = 0
        if action == 3:
            raise_amount = self.get_raise_amount(env, player_id, raise_logits)

        return action, raise_amount, action_logits, value
