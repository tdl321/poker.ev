# Neural Network Poker Agent System

A multi-agent reinforcement learning system for training neural network poker players with different risk profiles.

## Overview

This system implements neural network agents that learn to play poker through self-play. The agents use policy gradient methods and compete against each other with different risk preferences (risk-averse, risk-neutral, and risk-seeking).

## Files

### Core Components

1. **pokernew.py** - Poker game engine
   - `PokerEnv` class implementing Texas Hold'em mechanics
   - Hand evaluation, betting rounds, blinds, antes
   - Side pot handling and showdown logic
   - Enhanced action tracking and can_act state management

2. **poker_agent.py** - Neural network agent
   - `PokerAgent` class (PyTorch nn.Module)
   - Input: 44-dimensional state vector
   - Outputs: action logits (4 actions), raise amount logits (4 buckets), state value
   - Automatic action masking for illegal moves

3. **poker_env_adapter.py** - Environment wrapper
   - `PokerEnvAdapter` class for standard RL interface
   - Methods: `reset()`, `step()`, `legal_actions()`, `showdown()`
   - Risk transformation functions:
     - `risk_averse_reward(r)` - logarithmic compression
     - `risk_neutral_reward(r)` - linear (no transformation)
     - `risk_seeking_reward(r)` - quadratic amplification

4. **train_agents.py** - Training loop
   - `MultiAgentPokerTrainer` class
   - Policy gradient training
   - Support for multiple agents with different risk profiles
   - Episode tracking and model saving/loading

### Test and Utility Scripts

5. **test_state_dim.py** - Verify state vector dimension
6. **test_training.py** - Quick test of training system

## State Representation

The state vector has 44 dimensions:
- **Card ranks** (7): Ranks of player's 2 cards + 5 community cards (padded with 0s)
- **Card suits** (7): Suits of player's 2 cards + 5 community cards (padded with 0s)
- **Player ID** (1): Current player index
- **Active players** (9): Binary flags for each player (padded to MAX_NUM_PLAYERS)
- **Pot** (1): Total chips in pot
- **Current bet** (1): Amount current player has bet this round
- **All bets** (9): Bet amounts for all players (padded to MAX_NUM_PLAYERS)
- **All money** (9): Chip stacks for all players (padded to MAX_NUM_PLAYERS)

Total: 14 + 1 + 9 + 2 + 9 + 9 = **44 dimensions**

## Actions

The agent can take 4 actions:
- **0 = Fold**: Forfeit the hand
- **1 = Check**: Pass without betting (legal only when no bet to call)
- **2 = Call**: Match the current bet
- **3 = Raise**: Increase the bet

### Raise Amounts

When raising, the agent selects from 4 buckets:
- **Bucket 0**: Small raise (25% of pot or 10 chips)
- **Bucket 1**: Medium raise (50% of pot or 20 chips)
- **Bucket 2**: Large raise (75% of pot or 30 chips)
- **Bucket 3**: All-in or pot-sized raise

## Neural Network Architecture

```
Input (44) → FC(128) → ReLU → FC(128) → ReLU → 3 heads:
  - Action head: FC(4) → action logits
  - Raise head: FC(4) → raise amount logits
  - Value head: FC(1) → state value estimate
```

## Training

### Quick Test (10 episodes)

```bash
cd /Users/tdl321/Poker.ev/model
python test_training.py
```

### Full Training (500 episodes)

```bash
cd /Users/tdl321/Poker.ev/model
python train_agents.py
```

### Configuration

Edit the main() function in `train_agents.py`:

```python
NUM_PLAYERS = 3        # Number of agents
ENDOWMENT = 1000       # Starting chips
STATE_DIM = 44         # State vector size (fixed)
HIDDEN_DIM = 128       # Hidden layer size
LEARNING_RATE = 0.001  # Adam learning rate
NUM_EPISODES = 500     # Training episodes
SMALL_BLIND = 10       # Small blind amount
BIG_BLIND = 20         # Big blind amount
```

## Risk Profiles

Agents are assigned risk profiles in round-robin fashion:

1. **Risk-Neutral** (Agent 0)
   - Linear reward transformation
   - Balanced play style

2. **Risk-Averse** (Agent 1)
   - Logarithmic reward compression
   - Prefers consistent small wins over big risks

3. **Risk-Seeking** (Agent 2)
   - Quadratic reward amplification
   - Willing to take big risks for big rewards

## Training Algorithm

1. **Episode Generation**
   - Reset environment, deal cards
   - For each betting round (Pre-Flop, Flop, Turn, River):
     - Each agent selects action using current policy
     - Execute action in environment
     - Store state, action, raise amount
   - Showdown determines final rewards

2. **Policy Update** (Policy Gradient)
   - Transform rewards using agent's risk function
   - Recompute forward pass to get action logits with gradients
   - Compute policy loss: `-log_prob(action) * return`
   - Backpropagate and update weights

3. **Repeat** for specified number of episodes

## Saving and Loading Models

Models are automatically saved at the end of training:

```python
# Saved as: poker_agent_{id}_{risk_profile}.pt
poker_agent_0_neutral.pt
poker_agent_1_averse.pt
poker_agent_2_seeking.pt
```

To load models:

```python
trainer = MultiAgentPokerTrainer(...)
trainer.load_agents(filename_prefix="poker_agent")
```

## Training Results (500 Episodes)

**Latest Training Run:** November 9, 2025

```
Final Performance (last 100 episodes):
------------------------------------------------------------
  Agent 0 (neutral ): Avg =     1.80, Total =        861
  Agent 1 (averse  ): Avg =     9.30, Total =       4980
  Agent 2 (seeking ): Avg =    18.90, Total =       9159
```

**Key Findings:**
- 🏆 **Risk-seeking agent performed best** (18.90 avg reward)
- 📊 Risk-averse agent showed consistent, stable performance
- ⚠️ Risk-neutral agent underperformed other profiles

**Trained Models Saved:**
- `poker_agent_0_neutral.pt` (95 KB)
- `poker_agent_1_averse.pt` (95 KB)
- `poker_agent_2_seeking.pt` (95 KB)

See `TRAINING_RESULTS.md` for detailed analysis.

## Key Features

✅ **Multi-Agent Learning** - Agents learn through self-play competition
✅ **Risk Profiles** - Different reward transformations for diverse strategies
✅ **Legal Action Masking** - Automatic filtering of illegal moves
✅ **Side Pot Handling** - Proper all-in and side pot mechanics
✅ **Policy Gradient Training** - Standard REINFORCE algorithm
✅ **Fixed State Representation** - Consistent 44-dim vector across all game phases
✅ **Model Persistence** - Save and load trained agents

## Requirements

- Python 3.7+
- PyTorch
- NumPy

## Future Enhancements

- Advantage Actor-Critic (A2C) for better training stability
- Experience replay buffer
- Multi-hand episodes for variance reduction
- Opponent modeling
- Bluffing detection metrics
- Tournament mode with elimination

## Notes

- The poker engine uses a simplified hand evaluator
- All agents start with equal chip stacks at the beginning of each episode
- Training is done via self-play (agents play against each other)
- The state vector is normalized for better neural network training
