# poker.ev - AI Poker Application

A production-quality Texas Hold'Em poker game that combines:
- **texasholdem's** rock-solid game engine (fast evaluation, WSOP-compliant rules)
- **pyker's** beautiful 8-bit graphical interface
- **Advanced AI agents** with multiple playing styles

![poker.ev Screenshot](https://via.placeholder.com/800x600?text=poker.ev+Screenshot)

## Features

✅ **Production-Ready Game Engine**
- WSOP-compliant Texas Hold'Em rules
- Ultra-fast hand evaluation (Cactus Kev algorithm)
- Comprehensive game state management
- Side pots, all-ins, and edge cases handled correctly

✅ **Beautiful UI**
- Retro 8-bit aesthetic with pixel art
- Smooth 60 FPS gameplay
- Animated card dealing and chip movements
- Intuitive mouse and keyboard controls

✅ **Multiple AI Opponents**
- **Call Agent** - Always calls, never folds
- **Random Agent** - Makes random valid moves
- **Aggressive Agent** - Raises frequently (70% of the time)
- **Tight Agent** - Folds often, only plays strong hands

✅ **Extensible Architecture**
- Easy to add custom AI agents
- Clean separation of concerns
- Well-documented codebase

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
```bash
cd poker.ev
```

2. **Install dependencies**
```bash
# Install pygame and other dependencies
pip install -r requirements.txt

# Install texasholdem from the cloned repo
pip install -e ./texasholdem
```

3. **Verify installation**
```bash
python main.py
```

## Quick Start

### Run the default game (6 players)
```bash
python main.py
```

You'll be Player 0 at the bottom of the table, playing against 5 AI opponents.

### Run a simple 3-player game
```bash
python examples/simple_game.py
```

## Controls

### Mouse
- **Click action buttons** to make your move
- **Click and drag slider** to set raise amount
- **Click Confirm** to execute raise

### Keyboard Shortcuts
- **F** - Fold
- **C** - Call/Check
- **R** - Raise
- **A** - All In
- **ESC** - Cancel raise

## Project Structure

```
poker.ev/
├── poker_ev/              # Main package
│   ├── engine/            # Game engine wrapper
│   │   └── game_wrapper.py
│   ├── gui/               # Pygame GUI
│   │   ├── pygame_gui.py
│   │   ├── card_renderer.py
│   │   └── event_handler.py
│   ├── agents/            # AI agents
│   │   └── agent_manager.py
│   └── assets/            # Graphics (from pyker)
│       ├── cards/         # 52 card images
│       ├── buttons/       # Action buttons
│       └── fonts/         # Pixel fonts
├── texasholdem/           # Game engine (cloned)
├── pyker/                 # Reference (cloned)
├── examples/              # Example scripts
├── main.py                # Main entry point
└── requirements.txt       # Dependencies
```

## Architecture

poker.ev uses a 3-layer architecture:

```
┌─────────────────────────────────────┐
│      Poker.ev Application           │
└─────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┬────────┬────────┐
│ Engine │   AI   │  GUI   │
│ Layer  │ Layer  │ Layer  │
│        │        │        │
│texas   │texas   │ pyker  │
│holdem  │holdem  │(pygame)│
└────────┴────────┴────────┘
```

### Layer 1: Game Engine (texasholdem)
- Core game logic and rules
- Fast hand evaluation
- State management

### Layer 2: AI Layer
- Agent management
- Multiple AI strategies
- Extensible agent framework

### Layer 3: GUI Layer (pyker + custom)
- Pygame rendering
- Event handling
- User interaction

## Creating Custom AI Agents

You can easily create custom AI agents:

```python
from texasholdem import TexasHoldEm, ActionType
from typing import Tuple

def my_custom_agent(game: TexasHoldEm) -> Tuple[ActionType, int]:
    """
    Custom AI agent that implements your strategy

    Args:
        game: The texasholdem game instance

    Returns:
        Tuple of (ActionType, amount)
    """
    player_id = game.current_player

    # Get game state
    hand = game.get_hand(player_id)
    board = game.board
    pot = game.pot_total
    chips_to_call = game.chips_to_call(player_id)

    # Implement your strategy here
    # ...

    return ActionType.CALL, chips_to_call

# Register your agent
agent_manager.register_agent(1, my_custom_agent)
```

## Game Configuration

Customize the game setup in `main.py`:

```python
game = PokerGame(
    num_players=6,      # 2-9 players
    buyin=1000,         # Starting chips
    big_blind=10,       # Big blind amount
    small_blind=5       # Small blind amount
)
```

## Advanced Features

### Game History Export
```python
# Export game history to PGN format
game.export_history("./games/my_game.pgn")
```

### Access Full Game State
```python
state = game.get_game_state()
# Returns:
# {
#     'current_player': 0,
#     'hand_phase': HandPhase.FLOP,
#     'board': [Card(...), Card(...), Card(...)],
#     'pot': 150,
#     'players': [...],
#     'valid_actions': [ActionType.FOLD, ActionType.CALL, ActionType.RAISE],
#     'chips_to_call': 10,
#     'min_raise': 20,
# }
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black poker_ev/
```

### Type Checking
```bash
mypy poker_ev/
```

## Roadmap

### Phase 1: Core Features ✅ (Complete)
- [x] Basic game with GUI
- [x] Multiple AI agents
- [x] Card rendering
- [x] Event handling

### Phase 2: Enhanced Features (In Progress)
- [ ] GTO (Game Theory Optimal) agent
- [ ] Hand strength calculator
- [ ] Pot odds display
- [ ] Player statistics

### Phase 3: Advanced Features (Planned)
- [ ] Machine learning agents (RL)
- [ ] Training infrastructure
- [ ] Visual replay viewer
- [ ] Tournament mode
- [ ] Multi-table support

## Credits

### Built With
- **[texasholdem](https://github.com/SirRender00/texasholdem)** by SirRender00 - Production-ready poker engine
- **[pyker](https://github.com/nicolafan/pyker)** by nicolafan - Beautiful 8-bit graphics and assets
- **[Pygame](https://www.pygame.org/)** - Game development library

### Assets
- Card graphics by Michael Myers ([8-Bit Deck on itch.io](https://drawsgood.itch.io/8bit-deck-card-assets))
- Pixel fonts from Pixeloid font family

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

### Areas for Contribution
- New AI agents (GTO, ML-based)
- UI improvements
- Additional features (tournaments, statistics)
- Bug fixes and optimizations
- Documentation improvements

## Contact

- Issues: [GitHub Issues](https://github.com/yourusername/poker.ev/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/poker.ev/discussions)

---

**Enjoy playing poker.ev!** 🃏🎮
