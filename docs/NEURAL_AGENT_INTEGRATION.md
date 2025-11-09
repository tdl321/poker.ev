# Neural Network Agent Integration

This document explains how the trained neural network poker agents are integrated into the poker.ev GUI.

## Overview

The poker.ev application now supports **neural network AI opponents** trained using reinforcement learning. These agents use PyTorch models trained with policy gradient methods to make decisions based on game state.

## Architecture

### Components

1. **Training Environment** (`model/`)
   - `pokernew.py`: Custom poker environment for training
   - `poker_agent.py`: PyTorch neural network model
   - `train_agents.py`: Multi-agent training script
   - Trained models: `poker_agent_{id}_{risk_profile}.pt`

2. **Game Environment** (`poker_ev/engine/`)
   - `game_wrapper.py`: Wrapper for `texasholdem.TexasHoldEm` library
   - Production poker engine used by GUI

3. **Integration Layer** (`poker_ev/agents/`)
   - `state_converter.py`: Converts between game engines
   - `neural_agent.py`: Adapter wrapping trained models
   - `agent_manager.py`: Manages all AI agents

### Data Flow

```
TexasHoldEm Game State
         ↓
state_converter.py (converts to 44-dim vector)
         ↓
PokerAgent.act() (neural network inference)
         ↓
neural_agent.py (converts back to TexasHoldEm action)
         ↓
AgentManager (executes action in game)
```

## State Representation

The neural network expects a **44-dimensional state vector**:

```python
[
    # Card information (14 dimensions)
    ranks[0:7],          # Ranks of hand + community cards (padded to 7)
    suits[7:14],         # Suits of hand + community cards (padded to 7)

    # Player information (1 dimension)
    player_id[14],       # Current player ID

    # Game state (29 dimensions)
    active_players[15:24],  # Active status for each player (9 max)
    pot[24],                # Total pot size
    current_bet[25],        # Current bet for this player
    bets[26:35],            # All player bets (9 max)
    money[35:44]            # All player chip stacks (9 max)
]
```

### Card Format Conversion

**TexasHoldEm Library:**
- Cards: `Card` objects with `.rank` and `.suit` attributes
- Ranks: 0-12 (0=2, 12=A)
- Suits: Binary flags (1=♠, 2=♥, 4=♦, 8=♣)

**PokerEnv (Training):**
- Cards: `(rank, suit)` tuples
- Ranks: 2-14 (2-10, J=11, Q=12, K=13, A=14)
- Suits: 1=♠, 2=♥, 3=♦, 4=♣

The `state_converter.py` handles all conversions automatically.

## Risk Profiles

The system supports three risk profiles, each with different reward transformations during training:

### 1. **Risk-Neutral** (`neutral`)
- Linear reward: `R(x) = x`
- Balanced play
- Optimal for most situations

### 2. **Risk-Averse** (`averse`)
- Logarithmic reward: `R(x) = log(1 + |x|) * sign(x)`
- Conservative play
- Minimizes losses, cautious raises

### 3. **Risk-Seeking** (`seeking`)
- Quadratic reward: `R(x) = x²/100 * sign(x)`
- Aggressive play
- Maximizes big pots, frequent raises

## Usage

### Training Models

```bash
# Train models (creates 3 agents with different risk profiles)
cd model
python train_agents.py

# This creates:
# - poker_agent_0_neutral.pt
# - poker_agent_1_averse.pt
# - poker_agent_2_seeking.pt
```

### Running the GUI with Neural Agents

```bash
# Run with neural agents (default)
python main.py

# Or set environment variable
export USE_NEURAL_AGENTS=true
python main.py

# Run with rule-based agents (fallback)
export USE_NEURAL_AGENTS=false
python main.py
```

### Testing Integration

```bash
# Run integration test suite
python tests/test_neural_agent_integration.py
```

## Agent Selection

When you start the game, the system:

1. **Randomly selects** 5 risk profiles from `['neutral', 'averse', 'seeking']`
2. **Loads corresponding models** from `model/` directory
3. **Assigns to players** 1-5 (Player 0 is human)

Example distribution:
```
Player 1: neutral  <- poker_agent_0_neutral.pt
Player 2: seeking  <- poker_agent_2_seeking.pt
Player 3: averse   <- poker_agent_1_averse.pt
Player 4: neutral  <- poker_agent_0_neutral.pt
Player 5: seeking  <- poker_agent_2_seeking.pt
```

Each game has a **different random mix** for variety.

## Fallback Behavior

If neural agents fail to load (e.g., models not trained yet), the system automatically falls back to rule-based agents:

- **Call Agent**: Always calls or checks
- **Random Agent**: Random valid moves
- **Aggressive Agent**: Raises frequently
- **Tight Agent**: Folds often

## API Reference

### AgentManager

```python
from poker_ev.agents import AgentManager

agent_manager = AgentManager()

# Setup neural agents (automatic)
agent_manager.setup_neural_agents(
    num_players=6,
    human_player=0,
    model_dir="model/"  # Optional
)

# Register individual neural agent
agent_manager.register_neural_agent(
    player_id=1,
    model_path="model/poker_agent_0_neutral.pt",
    risk_profile="neutral"
)
```

### State Converter

```python
from poker_ev.agents.state_converter import texasholdem_to_pokerenv_state

# Convert game state to 44-dim vector
state = texasholdem_to_pokerenv_state(game, player_id=0)
# Returns: np.ndarray of shape (44,) and dtype float32
```

### Neural Agent Adapter

```python
from poker_ev.agents.neural_agent import create_neural_agent

# Create neural agent function
agent_func = create_neural_agent(
    model_path="model/poker_agent_0_neutral.pt",
    player_id=1,
    risk_profile="neutral"
)

# Use with TexasHoldEm
action, amount = agent_func(game)
```

## File Structure

```
poker.ev/
├── model/                          # Training environment
│   ├── pokernew.py                # PokerEnv class
│   ├── poker_agent.py             # PyTorch neural network
│   ├── poker_env_adapter.py       # RL environment adapter
│   ├── train_agents.py            # Training script
│   └── poker_agent_*.pt           # Trained model files
│
├── poker_ev/
│   ├── engine/
│   │   └── game_wrapper.py        # TexasHoldEm wrapper
│   │
│   ├── agents/
│   │   ├── agent_manager.py       # Agent coordination
│   │   ├── state_converter.py    # State format conversion
│   │   └── neural_agent.py        # Neural agent adapter
│   │
│   └── gui/
│       └── pygame_gui.py          # Main GUI
│
├── tests/
│   └── test_neural_agent_integration.py  # Integration tests
│
├── main.py                        # Entry point
└── docs/
    └── NEURAL_AGENT_INTEGRATION.md  # This file
```

## Performance Considerations

### Inference Speed
- Neural agents use **CPU inference** (fast enough for GUI)
- Each action takes ~5-20ms on modern CPU
- GPU not required for gameplay

### Memory Usage
- Each loaded model: ~500KB RAM
- 5 agents: ~2.5MB total
- Negligible compared to GUI overhead

## Troubleshooting

### Models Not Loading

**Symptom:** Game falls back to rule-based agents

**Solutions:**
1. Check model files exist: `ls model/poker_agent_*.pt`
2. Train models: `python model/train_agents.py`
3. Check model path in error message

### Import Errors

**Symptom:** `ImportError: cannot import PokerAgent`

**Solutions:**
1. Ensure PyTorch installed: `pip install torch`
2. Check model directory in Python path
3. Run from project root: `python main.py`

### State Conversion Errors

**Symptom:** `AssertionError: Expected shape (44,)`

**Solutions:**
1. Check TexasHoldEm version compatibility
2. Verify player count matches training (≤9 players)
3. Run test suite: `python tests/test_neural_agent_integration.py`

### Action Selection Errors

**Symptom:** Illegal actions or crashes during agent turns

**Solutions:**
1. Verify legal action masking in `neural_agent.py`
2. Check raise amount calculations
3. Enable debug mode to see agent decisions

## Future Improvements

### Potential Enhancements

1. **Online Learning**: Fine-tune models during gameplay
2. **Hand History Integration**: Use saved hands for model improvement
3. **Opponent Modeling**: Adapt to specific player styles
4. **Ensemble Agents**: Combine multiple models for better play
5. **GPU Acceleration**: Batch inference for faster action selection

### Model Training

For better performance:
- Train longer (>1000 episodes)
- Use larger networks (hidden_dim=256)
- Implement actor-critic instead of REINFORCE
- Add hand strength features to state vector

## References

- **TexasHoldEm Library**: https://github.com/fedden/poker_ai
- **Policy Gradient Methods**: Sutton & Barto, Reinforcement Learning
- **PyTorch Documentation**: https://pytorch.org/docs/

---

**Last Updated**: 2025-01-09
**Author**: poker.ev team
