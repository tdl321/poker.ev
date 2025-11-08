# poker.ev - AI Poker Application

A production-quality Texas Hold'Em poker game that combines:
- **[texasholdem](https://github.com/SirRender00/texasholdem)** - Rock-solid game engine (fast evaluation, WSOP-compliant rules)
- **[pyker](https://github.com/nicolafan/pyker)** - Beautiful 8-bit graphical interface and assets
- **Advanced AI agents** - Multiple playing styles and strategies

![poker.ev Screenshot](https://via.placeholder.com/800x600?text=poker.ev+Screenshot)

> **Note:** This project integrates code and assets from [texasholdem](https://github.com/SirRender00/texasholdem) (game engine) and [pyker](https://github.com/nicolafan/pyker) (UI/assets). See [Credits](#credits) section below for full attribution.

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

### Quick Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/poker.ev.git
cd poker.ev
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

That's it! All dependencies (pygame, numpy, texasholdem) will be installed automatically.

3. **Run the game**
```bash
python3 main.py
```

### Manual Setup (Alternative)

If you prefer to install dependencies manually:

```bash
pip install pygame numpy texasholdem Deprecated
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

---

## How to Play

### Game Setup

When you start poker.ev:
- **You are Player 0** (seated at the bottom of the table)
- **5 AI opponents** surround you with different playing styles
- Everyone starts with **$1,000** in chips
- Blinds are **$5 (small)** and **$10 (big)**

### Your AI Opponents

Each AI has a distinct personality:
- **Player 1: Call Agent** - Always calls, never folds or raises (predictable)
- **Player 2: Random Agent** - Unpredictable random moves
- **Player 3: Aggressive Agent** - Raises 70% of the time (dangerous)
- **Player 4: Tight Agent** - Folds 60% of the time, plays only strong hands
- **Player 5: Random Agent** - Unpredictable random moves

### Controls

#### Using Mouse
- **Click action buttons** to fold, check, call, or raise
- **Use slider** to select raise amount
- **Click confirm** to execute your raise
- All buttons highlight on hover

#### Keyboard Shortcuts
- **F** - Fold (give up your hand)
- **C** - Call/Check (match bet or stay in for free)
- **R** - Raise (increase the bet)
- **A** - All In (bet all your chips)
- **ESC** - Cancel raise slider

### Game Flow

#### 1. Pre-Flop
- You receive 2 hole cards (only you can see them)
- Small blind ($5) and big blind ($10) are posted automatically
- Action starts with the player after the big blind
- Decide: fold, call, or raise based on your hand strength

#### 2. The Flop
- 3 community cards are dealt face-up in the center
- These cards are shared by all players
- New betting round starts
- Evaluate your hand with the community cards

#### 3. The Turn
- 4th community card is dealt
- Another betting round
- Hands are becoming clearer

#### 4. The River
- 5th and final community card is dealt
- Final betting round
- Make your last decision

#### 5. Showdown
- Players reveal their hands
- Best 5-card poker hand wins the pot
- You can use any combination of your 2 cards + 5 community cards
- New hand begins automatically

### What You See On Screen

**Your Cards:**
- Bottom of screen, always face-up
- Combine with community cards to make your best hand

**Opponent Cards:**
- Face-down during play
- Revealed at showdown if they didn't fold

**Community Cards (The Board):**
- Center of table
- Shared by everyone
- Used to make your 5-card hand

**Pot Amount:**
- Total chips at stake
- Displayed in the center

**Player Info:**
- Each player shows their chip count
- Current bet amount for the round
- Status (active, folded, all-in)

**Dealer Button:**
- White button showing who's the dealer
- Rotates clockwise each hand
- Determines betting order

### Poker Hand Rankings

From best to worst:

1. **Royal Flush** - A♠ K♠ Q♠ J♠ 10♠ (unbeatable)
2. **Straight Flush** - Five cards in sequence, same suit (e.g., 9♥ 8♥ 7♥ 6♥ 5♥)
3. **Four of a Kind** - Four cards of same rank (e.g., K♠ K♥ K♦ K♣ A♠)
4. **Full House** - Three of a kind + a pair (e.g., 8♠ 8♥ 8♦ 3♣ 3♦)
5. **Flush** - Five cards of same suit (e.g., A♦ J♦ 9♦ 6♦ 2♦)
6. **Straight** - Five cards in sequence (e.g., 10♠ 9♥ 8♦ 7♣ 6♠)
7. **Three of a Kind** - Three cards of same rank (e.g., Q♠ Q♥ Q♦ K♠ 7♣)
8. **Two Pair** - Two different pairs (e.g., J♠ J♥ 5♦ 5♣ A♠)
9. **One Pair** - Two cards of same rank (e.g., 9♠ 9♥ K♦ 7♣ 3♠)
10. **High Card** - No pairs, highest card wins (e.g., A♠ K♥ 8♦ 5♣ 2♠)

### Strategy Tips

#### Playing Against AI Opponents

**Aggressive Agent (Player 3):**
- Will raise frequently (70% of the time)
- Don't get intimidated - call with strong hands
- Let them bet into you when you have a good hand
- Fold weak hands to save chips

**Tight Agent (Player 4):**
- Folds most hands
- If they stay in or raise, they likely have a strong hand
- Good target for bluffing
- Don't challenge them without a good hand

**Call Agent (Player 1):**
- Never folds, always calls
- Don't try to bluff them
- Value bet your strong hands
- Easy to extract chips from with good hands

**Random Agents (Players 2 & 5):**
- Completely unpredictable
- Standard poker strategy applies
- Watch for patterns (there may be some randomness)

#### General Poker Strategy

**Starting Hands:**
- **Strong:** AA, KK, QQ, AK (suited), AK
- **Good:** JJ, TT, AQ, AJ, KQ
- **Playable:** Medium pairs (99-66), suited connectors
- **Fold:** Weak hands (7-2, 9-3, etc.)

**Position Matters:**
- **Early Position:** Play only strong hands
- **Late Position:** Can play more hands, you act last
- **Button (Dealer):** Best position, play widest range

**Betting Guidelines:**
- **Pre-flop:** 3x big blind with good hands
- **Post-flop:** 50-75% of pot for value
- **Bluffing:** Occasional bluffs on scary boards
- **All-in:** Use sparingly, usually with very strong hands or as last resort

**Reading the Board:**
- **Flush possible?** Three+ cards of same suit
- **Straight possible?** Connected cards
- **Pairs on board?** Full house is possible
- **High cards?** Top pair may be winning

### Managing Your Bankroll

- Start conservative, don't risk all chips early
- Build your stack slowly
- Avoid going all-in unless necessary
- Play more aggressively when you have chip lead
- Tighten up when short-stacked

### Common Mistakes to Avoid

1. **Playing too many hands** - Be selective
2. **Chasing with weak draws** - Know when to fold
3. **Ignoring position** - Position is power
4. **Not adjusting to opponents** - Each AI plays differently
5. **Going on tilt** - Stay calm after bad beats

### Winning the Game

The goal is to **win all the chips** and eliminate all opponents. You win by:
- Having the best hand at showdown
- Making other players fold with strategic betting
- Outlasting opponents as they go bust

---

## Quick Reference Card

```
┌──────────────────────────────────────────┐
│ KEYBOARD SHORTCUTS                       │
├──────────────────────────────────────────┤
│ F   - Fold (give up hand)                │
│ C   - Call/Check (match bet/stay in)    │
│ R   - Raise (increase bet)               │
│ A   - All In (bet everything)            │
│ ESC - Cancel Raise                       │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ PLAYER POSITIONS                         │
├──────────────────────────────────────────┤
│ You:      Player 0 (Bottom)              │
│ AI #1:    Call Agent                     │
│ AI #2:    Random Agent                   │
│ AI #3:    Aggressive Agent ⚠️            │
│ AI #4:    Tight Agent                    │
│ AI #5:    Random Agent                   │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ STARTING CHIPS                           │
├──────────────────────────────────────────┤
│ Everyone:     $1,000                     │
│ Small Blind:  $5                         │
│ Big Blind:    $10                        │
└──────────────────────────────────────────┘
```

---

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
│   ├── assets/            # Graphics (from pyker)
│   │   ├── cards/         # 52 card images (8-bit style)
│   │   ├── buttons/       # Action buttons
│   │   ├── fonts/         # Pixel fonts
│   │   └── others/        # Dealer button, etc.
│   └── utils/             # Utility functions
├── claude/docs/           # Documentation
│   ├── INTEGRATION_PLAN.md
│   ├── REPOSITORY_COMPARISON.md
│   └── IMPLEMENTATION_STATUS.md
├── examples/              # Example scripts
│   └── simple_game.py
├── main.py                # Main entry point
├── test_components.py     # Component tests
├── requirements.txt       # Dependencies
├── setup.sh               # Setup script
└── README.md              # This file
```

## Architecture

poker.ev uses a 3-layer architecture that integrates texasholdem's engine with pyker's visual assets:

```
┌─────────────────────────────────────────────────────────────┐
│                  Poker.ev Application                       │
│                        (main.py)                            │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
    ┌─────────────┬─────────────┬─────────────┐
    │   Engine    │     AI      │     GUI     │
    │   Layer     │    Layer    │    Layer    │
    │             │             │             │
    │ PokerGame   │ AgentMgr    │ PygameGUI   │
    │  wrapper    │  + Custom   │  + Event    │
    │     ↓       │   Agents    │   Handler   │
    │ texasholdem │     ↓       │     ↓       │
    │   (pip)     │ texasholdem │ pyker assets│
    └─────────────┴─────────────┴─────────────┘
```

### Integration Details

#### Layer 1: Game Engine
**Source:** [texasholdem](https://github.com/SirRender00/texasholdem) (installed via pip)
- **Core Logic:** `TexasHoldEm` class handles all poker rules
- **Wrapper:** `PokerGame` (`poker_ev/engine/game_wrapper.py`)
  - Translates texasholdem's internal API to GUI-friendly format
  - Provides simplified methods: `get_game_state()`, `take_action()`, etc.
  - Handles API quirks and edge cases

#### Layer 2: AI Layer
**Source:** Custom + texasholdem agents
- **Manager:** `AgentManager` (`poker_ev/agents/agent_manager.py`)
- **Built-in Agents:** `random_agent`, `call_agent` from texasholdem
- **Custom Agents:** Aggressive, Tight (custom implementations)
- **Extensible:** Easy to add new AI strategies

#### Layer 3: GUI Layer
**Source:** [pyker](https://github.com/nicolafan/pyker) assets + custom code
- **Assets:** Cards, buttons, fonts from pyker (`poker_ev/assets/`)
- **Rendering:** `CardRenderer` (`poker_ev/gui/card_renderer.py`)
  - Converts texasholdem `Card` objects → pyker sprite filenames
  - Maps integer suit values (1,2,4,8) → sprite names ('S','H','D','C')
- **Interface:** `PygameGUI` (`poker_ev/gui/pygame_gui.py`)
  - Custom pygame interface (not from pyker)
  - Uses pyker's visual style and assets
- **Events:** `EventHandler` (`poker_ev/gui/event_handler.py`)
  - Keyboard/mouse → game actions

### Data Flow Example

```
User clicks "RAISE" button
         ↓
EventHandler detects click
         ↓
Returns ActionType.RAISE + amount
         ↓
PygameGUI calls game.take_action()
         ↓
PokerGame wrapper validates action
         ↓
Calls engine.take_action() (texasholdem)
         ↓
texasholdem updates game state
         ↓
PygameGUI calls game.get_game_state()
         ↓
PokerGame queries engine.pots, engine.board, etc.
         ↓
Returns formatted state dict
         ↓
CardRenderer converts Cards to sprite paths
         ↓
PygameGUI renders updated table
         ↓
User sees new game state
```

### Key Integration Challenges Solved

1. **Card Representation**
   - texasholdem uses `Card` objects with integer suits (1,2,4,8)
   - pyker expects string filenames like "AS.png", "KH.png"
   - **Solution:** `CardRenderer` maps between the two

2. **Action Validation**
   - texasholdem uses `get_available_moves()` returning `MoveIterator`
   - GUI needs simple list of valid actions
   - **Solution:** `PokerGame._get_valid_actions()` extracts action types

3. **Pot Calculation**
   - texasholdem stores pots separately from current bets
   - GUI needs total pot including current round
   - **Solution:** Sum pot amounts + player bets

4. **Player State**
   - texasholdem uses `PlayerState` enum (SKIP, OUT, IN, TO_CALL, ALL_IN)
   - GUI needs simple active/folded/all-in flags
   - **Solution:** Map PlayerState values to GUI-friendly booleans

### Why Not Fork?

Instead of forking either project, poker.ev creates a **composition** architecture:
- ✅ **Upgradable:** Can update texasholdem via `pip install --upgrade`
- ✅ **Modular:** Each layer can be swapped independently
- ✅ **Clean Attribution:** Clear what's original vs. integrated
- ✅ **Testable:** Each layer can be tested independently

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

This project stands on the shoulders of giants. poker.ev integrates and extends code from these excellent open-source projects:

#### **[texasholdem](https://github.com/SirRender00/texasholdem)** by SirRender00
- **License:** MIT
- **Used for:** Core game engine, hand evaluation, game state management
- **What we use:**
  - `TexasHoldEm` game engine class
  - `Card`, `ActionType`, `HandPhase`, `PlayerState` types
  - Built-in agents (`random_agent`, `call_agent`)
  - `get_available_moves()`, `min_raise()`, and other API methods
- **Installed via:** pip (`pip install texasholdem`)
- **Repository:** https://github.com/SirRender00/texasholdem
- **Description:** Production-ready Texas Hold'Em poker engine with ultra-fast hand evaluation using the Cactus Kev algorithm. WSOP-compliant rules.

#### **[pyker](https://github.com/nicolafan/pyker)** by nicolafan
- **License:** MIT
- **Used for:** UI inspiration, graphical assets, pixel art design
- **What we use:**
  - 8-bit style card images (all 52 cards + backs)
  - Action button graphics (fold, call, check, raise)
  - Pixel fonts (PixeloidSans, PixeloidMono)
  - Dealer button and chip graphics
  - Overall retro aesthetic design
- **Assets location:** `poker_ev/assets/`
- **Repository:** https://github.com/nicolafan/pyker
- **Description:** Beautiful pygame-based poker game with retro 8-bit graphics and clean architecture.

#### **[Pygame](https://www.pygame.org/)**
- **License:** LGPL
- **Used for:** Graphics rendering, event handling, game loop
- **Repository:** https://github.com/pygame/pygame

### Original Asset Creators

- **Card Graphics:** Michael Myers - [8-Bit Deck on itch.io](https://drawsgood.itch.io/8bit-deck-card-assets)
- **Pixel Fonts:** Pixeloid font family by [GGBotNet](https://ggbot.itch.io/pixeloid-font)

### What poker.ev Adds

This project is **not** a simple fork - it represents a significant integration and extension:

**Original Contributions:**
- Complete integration layer between texasholdem engine and pygame GUI
- `PokerGame` wrapper class for GUI-friendly API (`poker_ev/engine/game_wrapper.py`)
- `CardRenderer` for converting texasholdem cards to pyker sprites (`poker_ev/gui/card_renderer.py`)
- `EventHandler` for pygame event processing (`poker_ev/gui/event_handler.py`)
- `PygameGUI` main interface combining both projects (`poker_ev/gui/pygame_gui.py`)
- `AgentManager` with multiple AI personalities (`poker_ev/agents/agent_manager.py`)
  - Aggressive agent (raises 70% of the time)
  - Tight agent (folds 60% of the time)
  - Extensible agent framework
- API bug fixes and improvements:
  - Fixed action validation using `get_available_moves()`
  - Fixed pot calculation to include player bets
  - Fixed card suit representation (integers vs strings)
  - Fixed player state checking
- Comprehensive test suite (`test_components.py`)
- Documentation and integration guides
- Example scripts and setup automation

**Why This Integration Matters:**
- **texasholdem** provides a bulletproof engine but no GUI
- **pyker** provides beautiful graphics but uses a custom game engine
- **poker.ev** combines the best of both: production game engine + beautiful UI

### Acknowledgments

Special thanks to:
- **[@SirRender00](https://github.com/SirRender00)** for creating the excellent texasholdem engine
- **[@nicolafan](https://github.com/nicolafan)** for the beautiful pyker graphics and design inspiration
- The Pygame community for the amazing game development library

## License

MIT License - see LICENSE file for details

**Note on Licenses:**
- This project (poker.ev) is released under MIT License
- texasholdem library: MIT License
- pyker assets and code: MIT License
- Pygame: LGPL

All dependencies respect their original licenses. See individual projects for details.

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
