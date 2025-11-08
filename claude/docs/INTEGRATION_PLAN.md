# Poker.ev Integration Plan
## Combining pyker's UI with texasholdem's AI Infrastructure

**Goal:** Create a production-quality AI poker application that leverages:
- **texasholdem's** rock-solid game engine, fast evaluation, and AI framework
- **pyker's** beautiful Pygame UI, 8-bit graphics, and visual components

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Component Mapping](#component-mapping)
3. [Integration Strategy](#integration-strategy)
4. [Project Structure](#project-structure)
5. [Implementation Phases](#implementation-phases)
6. [Code Examples](#code-examples)
7. [Technical Challenges](#technical-challenges)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Plan](#deployment-plan)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Poker.ev                             │
│                   AI Poker Application                       │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Game       │    │   AI/Agent   │    │   GUI        │
│   Engine     │◄───│   Layer      │───►│   Layer      │
│              │    │              │    │              │
│ texasholdem  │    │ texasholdem  │    │   pyker      │
│   (core)     │    │  (agents)    │    │ (visuals)    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ - Card eval  │    │ - Random AI  │    │ - Pygame     │
│ - Game state │    │ - Call AI    │    │ - Cards      │
│ - Rules      │    │ - Custom AI  │    │ - Buttons    │
│ - History    │    │ - GTO AI     │    │ - Fonts      │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Layer Responsibilities

#### Layer 1: Game Engine (texasholdem)
**Purpose:** Core game logic, state management, rules enforcement

**Responsibilities:**
- Manage game state (chips, pots, players, hands)
- Enforce Texas Hold'Em rules (WSOP compliant)
- Handle betting rounds and action validation
- Fast hand evaluation (Cactus Kev algorithm)
- Game history export/import (PGN format)
- Side pot calculations
- All-in logic

**Why texasholdem:**
- ✅ Production-tested (16 test files, CI/CD)
- ✅ 10-100x faster hand evaluation
- ✅ Handles edge cases correctly
- ✅ Comprehensive API
- ✅ No game logic bugs

#### Layer 2: AI/Agent Layer (texasholdem + custom)
**Purpose:** AI opponents with varying skill levels

**Responsibilities:**
- Provide built-in agents (random, call)
- Custom AI implementation (GTO, Nash equilibrium)
- Machine learning integration (RL, neural networks)
- Agent evaluation and testing
- Strategy evolution

**Why texasholdem:**
- ✅ Clean agent interface
- ✅ Full game state access
- ✅ Easy to extend
- ✅ Scriptable for training

#### Layer 3: GUI Layer (pyker + custom)
**Purpose:** Visual presentation and user interaction

**Responsibilities:**
- Render game state visually
- Handle user input (clicks, keyboard)
- Animate card dealing and actions
- Display player information
- Show pot, bets, community cards
- Provide betting interface

**Why pyker:**
- ✅ Beautiful 8-bit aesthetic
- ✅ Complete asset library (52 cards, buttons, fonts)
- ✅ Pygame-based (well-established)
- ✅ Easy to customize

---

## Component Mapping

### From texasholdem to poker.ev

| texasholdem Component | Use in poker.ev | Status |
|-----------------------|-----------------|--------|
| `TexasHoldEm` class | Core game engine | ✅ Use as-is |
| `Card` class | Card representation | ✅ Use as-is |
| `ActionType` enum | Player actions | ✅ Use as-is |
| `HandPhase` enum | Game phases | ✅ Use as-is |
| `PlayerState` class | Player tracking | ✅ Use as-is |
| `evaluator` module | Hand evaluation | ✅ Use as-is |
| `agents.random_agent` | AI opponent | ✅ Use as-is |
| `agents.call_agent` | AI opponent | ✅ Use as-is |
| `History` class | Game replay | ✅ Use as-is |
| `TextGUI` class | CLI interface | ❌ Replace with Pygame |

### From pyker to poker.ev

| pyker Component | Use in poker.ev | Status |
|----------------|-----------------|--------|
| Card sprites (52 images) | Visual card display | ✅ Use as-is |
| Button sprites | Action buttons | ✅ Use as-is |
| Pixel fonts | Text rendering | ✅ Use as-is |
| Dealer chip graphic | Position marker | ✅ Use as-is |
| `load_assets()` | Asset loading | ✅ Adapt |
| GUI layout logic | Screen positioning | ✅ Adapt |
| Pygame event handling | User input | ✅ Adapt |
| `Card` class | Card model | ❌ Use texasholdem's |
| `Game` class | Game logic | ❌ Use texasholdem's |
| `hands_checker` | Hand evaluation | ❌ Use texasholdem's |
| Dummy AI | AI logic | ❌ Use texasholdem's |

### New Components to Build

| Component | Purpose | Priority |
|-----------|---------|----------|
| `PygameGUI` class | Pygame GUI adapter for texasholdem | 🔴 Critical |
| `CardRenderer` class | Convert texasholdem Card → pyker sprite | 🔴 Critical |
| `GameStateRenderer` | Render texasholdem game state | 🔴 Critical |
| `EventHandler` class | Convert Pygame events → texasholdem actions | 🔴 Critical |
| `AdvancedAgent` class | GTO/Nash AI implementation | 🟡 High |
| `MLAgent` class | Machine learning AI | 🟢 Medium |
| `ReplayViewer` class | Visual replay of PGN files | 🟢 Medium |
| `StatisticsTracker` | Player stats and analytics | 🔵 Low |

---

## Integration Strategy

### Phase 1: Core Integration (Week 1-2)

**Goal:** Get texasholdem running with pyker's visuals

#### Step 1.1: Setup Project Structure
```bash
poker.ev/
├── poker_ev/                    # Main package
│   ├── __init__.py
│   ├── engine/                  # texasholdem wrapper
│   │   ├── __init__.py
│   │   └── game_wrapper.py
│   ├── gui/                     # Pygame GUI
│   │   ├── __init__.py
│   │   ├── pygame_gui.py        # Main GUI class
│   │   ├── card_renderer.py     # Card → sprite mapping
│   │   ├── state_renderer.py    # Game state rendering
│   │   └── event_handler.py     # Input handling
│   ├── agents/                  # AI agents
│   │   ├── __init__.py
│   │   ├── basic.py             # Wrapper for texasholdem agents
│   │   └── advanced.py          # Custom AI
│   └── assets/                  # From pyker
│       ├── cards/               # 52 card images
│       ├── buttons/             # Action buttons
│       ├── fonts/               # Pixel fonts
│       └── others/              # Dealer chip, etc.
├── tests/
├── examples/
├── docs/
└── requirements.txt
```

#### Step 1.2: Create Adapter Layer
```python
# poker_ev/engine/game_wrapper.py
from texasholdem import TexasHoldEm, Card, ActionType, HandPhase
from typing import List, Tuple, Optional

class PokerGame:
    """Wrapper around texasholdem.TexasHoldEm with GUI-friendly interface"""

    def __init__(self, num_players: int = 6, buyin: int = 1000,
                 big_blind: int = 10, small_blind: int = 5):
        self.engine = TexasHoldEm(
            buyin=buyin,
            big_blind=big_blind,
            small_blind=small_blind,
            max_players=num_players
        )
        self.num_players = num_players

    def start_new_hand(self):
        """Start a new hand"""
        self.engine.start_hand()

    def get_game_state(self) -> dict:
        """Get complete game state for rendering"""
        return {
            'current_player': self.engine.current_player,
            'hand_phase': self.engine.hand_phase,
            'board': self.engine.board,
            'pot': self.engine.pot_total,
            'players': self._get_player_states(),
            'valid_actions': self._get_valid_actions(),
            'chips_to_call': self.engine.chips_to_call(self.engine.current_player),
        }

    def _get_player_states(self) -> List[dict]:
        """Get state for all players"""
        states = []
        for player_id in range(self.num_players):
            if not self.engine.in_hand(player_id):
                states.append({'active': False})
                continue

            states.append({
                'active': True,
                'id': player_id,
                'chips': self.engine.players[player_id].chips,
                'bet': self.engine.player_bet_amount(player_id),
                'hand': self.engine.get_hand(player_id),
                'folded': self.engine.folded(player_id),
                'all_in': self.engine.all_in(player_id),
            })
        return states

    def _get_valid_actions(self) -> List[ActionType]:
        """Get valid actions for current player"""
        actions = []
        player = self.engine.current_player

        if self.engine.valid_action(player, ActionType.FOLD):
            actions.append(ActionType.FOLD)
        if self.engine.valid_action(player, ActionType.CHECK):
            actions.append(ActionType.CHECK)
        if self.engine.valid_action(player, ActionType.CALL):
            actions.append(ActionType.CALL)
        if self.engine.valid_action(player, ActionType.RAISE):
            actions.append(ActionType.RAISE)
        if self.engine.valid_action(player, ActionType.ALL_IN):
            actions.append(ActionType.ALL_IN)

        return actions

    def take_action(self, action: ActionType, amount: int = 0):
        """Execute an action"""
        self.engine.take_action(action, total=amount)

    def is_hand_running(self) -> bool:
        """Check if current hand is still active"""
        return self.engine.is_hand_running()

    def is_game_running(self) -> bool:
        """Check if game is still active"""
        return self.engine.is_game_running()
```

#### Step 1.3: Create Card Renderer
```python
# poker_ev/gui/card_renderer.py
import pygame
from texasholdem import Card
from typing import Dict

class CardRenderer:
    """Convert texasholdem Card objects to pyker sprites"""

    def __init__(self, card_sprites: Dict[str, pygame.Surface]):
        self.card_sprites = card_sprites

    def card_to_sprite_name(self, card: Card) -> str:
        """
        Convert texasholdem Card to pyker sprite name

        texasholdem: Card("Kd") → rank=11, suit=diamonds
        pyker: "KD.png"
        """
        # Rank mapping (texasholdem uses 0-12, pyker uses 2-A)
        rank_map = {
            0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7',
            6: '8', 7: '9', 8: '10', 9: 'J', 10: 'Q', 11: 'K', 12: 'A'
        }

        # Suit mapping
        suit_map = {
            'spades': 'S',
            'hearts': 'H',
            'diamonds': 'D',
            'clubs': 'C'
        }

        rank_str = rank_map[card.rank]
        suit_str = suit_map[card.suit]

        return f"{rank_str}{suit_str}"

    def get_card_sprite(self, card: Card) -> pygame.Surface:
        """Get sprite for a card"""
        sprite_name = self.card_to_sprite_name(card)
        return self.card_sprites.get(sprite_name)

    def get_card_back(self) -> pygame.Surface:
        """Get card back sprite"""
        return self.card_sprites.get("back_red")
```

### Phase 2: GUI Implementation (Week 2-3)

#### Main GUI Class
```python
# poker_ev/gui/pygame_gui.py
import pygame
from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.gui.card_renderer import CardRenderer
from poker_ev.gui.event_handler import EventHandler
from texasholdem import ActionType
from typing import Optional

class PygameGUI:
    """Main Pygame GUI for poker.ev"""

    def __init__(self, game: PokerGame, window_size: tuple = (1200, 800)):
        pygame.init()
        self.game = game
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Poker.ev - AI Poker")

        # Load assets from pyker
        self.load_assets()

        # Initialize renderers
        self.card_renderer = CardRenderer(self.card_sprites)
        self.event_handler = EventHandler(self)

        # GUI state
        self.selected_action: Optional[ActionType] = None
        self.raise_amount: int = 0

        # Colors
        self.BG_COLOR = (53, 101, 77)  # Poker table green
        self.TEXT_COLOR = (255, 255, 255)

    def load_assets(self):
        """Load all assets from pyker"""
        # This is adapted from pyker's load_assets()
        assets_dir = "poker_ev/assets"

        self.card_sprites = {}
        # Load card images...

        self.button_sprites = {}
        # Load button images...

        self.fonts = {}
        # Load fonts...

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True

        while running and self.game.is_game_running():
            # Start new hand if needed
            if not self.game.is_hand_running():
                self.game.start_new_hand()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.event_handler.handle_event(event)

            # Render
            self.render()

            pygame.display.flip()
            clock.tick(60)  # 60 FPS

        pygame.quit()

    def render(self):
        """Render the current game state"""
        self.screen.fill(self.BG_COLOR)

        state = self.game.get_game_state()

        # Render components
        self.render_table()
        self.render_community_cards(state['board'])
        self.render_pot(state['pot'])
        self.render_players(state['players'])
        self.render_action_buttons(state['valid_actions'])
        self.render_current_player_indicator(state['current_player'])

    def render_table(self):
        """Draw poker table"""
        # Ellipse for table
        table_rect = pygame.Rect(100, 150, 1000, 500)
        pygame.draw.ellipse(self.screen, (34, 80, 57), table_rect)
        pygame.draw.ellipse(self.screen, (200, 200, 200), table_rect, 3)

    def render_community_cards(self, board: list):
        """Render the community cards"""
        x_start = 400
        y = 350
        spacing = 120

        for i, card in enumerate(board):
            sprite = self.card_renderer.get_card_sprite(card)
            x = x_start + i * spacing
            self.screen.blit(sprite, (x, y))

    def render_pot(self, pot_amount: int):
        """Render pot amount"""
        font = self.fonts['medium']
        text = font.render(f"Pot: ${pot_amount}", True, self.TEXT_COLOR)
        text_rect = text.get_rect(center=(600, 320))
        self.screen.blit(text, text_rect)

    def render_players(self, players: list):
        """Render all players around the table"""
        # Position players in circle around table
        positions = [
            (600, 650),   # Bottom (player 0 - human)
            (200, 550),   # Left bottom
            (100, 350),   # Left middle
            (200, 150),   # Left top
            (600, 100),   # Top
            (1000, 150),  # Right top
            (1100, 350),  # Right middle
            (1000, 550),  # Right bottom
        ]

        for i, player in enumerate(players):
            if not player.get('active'):
                continue

            x, y = positions[i]
            self.render_player(player, x, y, is_human=(i == 0))

    def render_player(self, player: dict, x: int, y: int, is_human: bool):
        """Render a single player"""
        # Player box
        box_rect = pygame.Rect(x - 75, y - 50, 150, 100)
        pygame.draw.rect(self.screen, (40, 40, 40), box_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), box_rect, 2)

        # Player name
        font = self.fonts['small']
        name = f"Player {player['id']}" if not is_human else "You"
        name_text = font.render(name, True, self.TEXT_COLOR)
        self.screen.blit(name_text, (x - 65, y - 40))

        # Chips
        chips_text = font.render(f"${player['chips']}", True, (255, 215, 0))
        self.screen.blit(chips_text, (x - 65, y - 20))

        # Current bet
        if player['bet'] > 0:
            bet_text = font.render(f"Bet: ${player['bet']}", True, (255, 100, 100))
            self.screen.blit(bet_text, (x - 65, y))

        # Cards (only show for human player)
        if is_human and 'hand' in player:
            for i, card in enumerate(player['hand']):
                sprite = self.card_renderer.get_card_sprite(card)
                # Scale down for player display
                sprite = pygame.transform.scale(sprite, (60, 84))
                self.screen.blit(sprite, (x - 70 + i * 70, y + 20))
        elif 'hand' in player:
            # Show card backs for AI players
            for i in range(2):
                sprite = self.card_renderer.get_card_back()
                sprite = pygame.transform.scale(sprite, (60, 84))
                self.screen.blit(sprite, (x - 70 + i * 70, y + 20))

        # Status indicators
        if player.get('folded'):
            status_text = font.render("FOLDED", True, (255, 0, 0))
            self.screen.blit(status_text, (x - 40, y + 35))
        elif player.get('all_in'):
            status_text = font.render("ALL IN", True, (255, 215, 0))
            self.screen.blit(status_text, (x - 40, y + 35))

    def render_action_buttons(self, valid_actions: list):
        """Render action buttons for human player"""
        button_y = 720
        button_spacing = 140
        button_start_x = 200

        action_names = {
            ActionType.FOLD: 'fold',
            ActionType.CHECK: 'check',
            ActionType.CALL: 'call',
            ActionType.RAISE: 'raise',
            ActionType.ALL_IN: 'allin',
        }

        for i, action in enumerate(valid_actions):
            button_name = action_names.get(action, 'unknown')
            if button_name in self.button_sprites:
                sprite = self.button_sprites[button_name]
                x = button_start_x + i * button_spacing
                self.screen.blit(sprite, (x, button_y))

                # Store button rect for click detection
                button_rect = pygame.Rect(x, button_y, sprite.get_width(), sprite.get_height())
                self.event_handler.register_button(action, button_rect)

    def render_current_player_indicator(self, current_player: int):
        """Highlight current player"""
        # Draw arrow or highlight around current player
        pass

    def handle_action_click(self, action: ActionType):
        """Handle action button click"""
        if action == ActionType.RAISE:
            # Show raise amount input
            self.show_raise_input()
        else:
            # Execute action
            self.game.take_action(action)

    def show_raise_input(self):
        """Show UI for entering raise amount"""
        # Simple implementation - can be enhanced
        pass
```

#### Event Handler
```python
# poker_ev/gui/event_handler.py
import pygame
from texasholdem import ActionType
from typing import Dict

class EventHandler:
    """Handle Pygame events and convert to game actions"""

    def __init__(self, gui):
        self.gui = gui
        self.button_rects: Dict[ActionType, pygame.Rect] = {}

    def register_button(self, action: ActionType, rect: pygame.Rect):
        """Register a clickable button"""
        self.button_rects[action] = rect

    def handle_event(self, event: pygame.event.Event):
        """Process a Pygame event"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_keypress(event.key)

    def handle_click(self, pos: tuple):
        """Handle mouse click"""
        for action, rect in self.button_rects.items():
            if rect.collidepoint(pos):
                self.gui.handle_action_click(action)
                break

    def handle_keypress(self, key: int):
        """Handle keyboard input"""
        # Shortcuts
        if key == pygame.K_f:
            self.gui.handle_action_click(ActionType.FOLD)
        elif key == pygame.K_c:
            self.gui.handle_action_click(ActionType.CALL)
        elif key == pygame.K_r:
            self.gui.handle_action_click(ActionType.RAISE)
```

### Phase 3: AI Integration (Week 3-4)

#### Agent Manager
```python
# poker_ev/agents/agent_manager.py
from texasholdem import TexasHoldEm, ActionType
from texasholdem.agents import random_agent, call_agent
from typing import Tuple, Callable

AgentFunc = Callable[[TexasHoldEm], Tuple[ActionType, int]]

class AgentManager:
    """Manage AI agents for poker.ev"""

    def __init__(self):
        self.agents: dict[int, AgentFunc] = {}

    def register_agent(self, player_id: int, agent_func: AgentFunc):
        """Register an AI agent for a player"""
        self.agents[player_id] = agent_func

    def get_action(self, game: TexasHoldEm, player_id: int) -> Tuple[ActionType, int]:
        """Get action from AI agent"""
        if player_id in self.agents:
            return self.agents[player_id](game)
        else:
            # Default to random
            return random_agent(game)

    # Built-in agents from texasholdem
    @staticmethod
    def random_agent(game: TexasHoldEm) -> Tuple[ActionType, int]:
        return random_agent(game)

    @staticmethod
    def call_agent(game: TexasHoldEm) -> Tuple[ActionType, int]:
        return call_agent(game)
```

#### Advanced AI (GTO)
```python
# poker_ev/agents/advanced.py
from texasholdem import TexasHoldEm, ActionType, evaluate
from typing import Tuple
import random

class GTOAgent:
    """
    Game Theory Optimal agent
    Uses preflop charts, hand strength, and pot odds
    """

    def __init__(self):
        # Load preflop charts, GTO strategy tables, etc.
        pass

    def get_action(self, game: TexasHoldEm) -> Tuple[ActionType, int]:
        """Get GTO-based action"""
        player_id = game.current_player
        hand = game.get_hand(player_id)
        board = game.board

        # Calculate hand strength
        if len(board) >= 3:
            hand_rank = evaluate(hand, board)
            hand_strength = 1 - (hand_rank / 7462)  # Normalize to 0-1
        else:
            # Preflop - use starting hand strength
            hand_strength = self.preflop_hand_strength(hand)

        # Calculate pot odds
        pot_total = game.pot_total
        chips_to_call = game.chips_to_call(player_id)

        if chips_to_call == 0:
            # Free to check
            return self.check_or_bet(game, hand_strength)
        else:
            # Need to call or fold
            pot_odds = chips_to_call / (pot_total + chips_to_call)
            return self.call_fold_raise_decision(game, hand_strength, pot_odds)

    def preflop_hand_strength(self, hand: list) -> float:
        """Estimate preflop hand strength"""
        # Simplified - use Chen formula or preflop equity tables
        # Return value between 0 and 1
        return 0.5

    def check_or_bet(self, game: TexasHoldEm, strength: float) -> Tuple[ActionType, int]:
        """Decide whether to check or bet"""
        if strength > 0.7:
            # Strong hand - bet
            min_raise = game.chips_to_call(game.current_player) + game.big_blind
            raise_amount = int(game.pot_total * 0.5)  # 50% pot bet
            raise_amount = max(raise_amount, min_raise)
            return ActionType.RAISE, raise_amount
        else:
            # Weak hand - check
            return ActionType.CHECK, 0

    def call_fold_raise_decision(self, game: TexasHoldEm,
                                  strength: float, pot_odds: float) -> Tuple[ActionType, int]:
        """Decide call/fold/raise based on hand strength and pot odds"""
        if strength > pot_odds * 2:
            # Strong hand - raise
            raise_amount = int(game.pot_total * 0.75)
            return ActionType.RAISE, raise_amount
        elif strength > pot_odds:
            # Medium hand - call
            return ActionType.CALL, game.chips_to_call(game.current_player)
        else:
            # Weak hand - fold
            return ActionType.FOLD, 0
```

### Phase 4: Main Application (Week 4)

```python
# main.py
from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.gui.pygame_gui import PygameGUI
from poker_ev.agents.agent_manager import AgentManager
from poker_ev.agents.advanced import GTOAgent

def main():
    """Run poker.ev application"""

    # Create game
    game = PokerGame(
        num_players=6,
        buyin=1000,
        big_blind=10,
        small_blind=5
    )

    # Setup AI agents
    agent_manager = AgentManager()
    gto_agent = GTOAgent()

    # Player 0 is human (no agent)
    # Players 1-5 are AI
    agent_manager.register_agent(1, AgentManager.random_agent)
    agent_manager.register_agent(2, AgentManager.call_agent)
    agent_manager.register_agent(3, gto_agent.get_action)
    agent_manager.register_agent(4, AgentManager.random_agent)
    agent_manager.register_agent(5, gto_agent.get_action)

    # Create GUI
    gui = PygameGUI(game, agent_manager)

    # Run game
    gui.run()

if __name__ == "__main__":
    main()
```

---

## Project Structure

### Final Directory Layout

```
poker.ev/
├── README.md
├── INTEGRATION_PLAN.md
├── REPOSITORY_COMPARISON.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── setup.py
│
├── poker_ev/                          # Main package
│   ├── __init__.py
│   │
│   ├── engine/                        # Game engine (texasholdem wrapper)
│   │   ├── __init__.py
│   │   ├── game_wrapper.py            # PokerGame class
│   │   └── state_manager.py           # Game state utilities
│   │
│   ├── gui/                           # Pygame GUI
│   │   ├── __init__.py
│   │   ├── pygame_gui.py              # Main GUI class
│   │   ├── card_renderer.py           # Card → sprite conversion
│   │   ├── state_renderer.py          # Game state rendering
│   │   ├── event_handler.py           # Input handling
│   │   ├── components/                # UI components
│   │   │   ├── __init__.py
│   │   │   ├── player_widget.py
│   │   │   ├── pot_widget.py
│   │   │   ├── action_buttons.py
│   │   │   └── raise_slider.py
│   │   └── animations/                # Animations
│   │       ├── __init__.py
│   │       ├── card_deal.py
│   │       └── chip_movement.py
│   │
│   ├── agents/                        # AI agents
│   │   ├── __init__.py
│   │   ├── agent_manager.py           # Agent coordination
│   │   ├── basic.py                   # Wrapper for texasholdem agents
│   │   ├── advanced.py                # GTO agent
│   │   ├── ml/                        # Machine learning agents
│   │   │   ├── __init__.py
│   │   │   ├── rl_agent.py            # Reinforcement learning
│   │   │   ├── neural_agent.py        # Neural network
│   │   │   └── trainer.py             # Training infrastructure
│   │   └── evaluation/                # Agent evaluation
│   │       ├── __init__.py
│   │       ├── evaluator.py
│   │       └── tournament.py
│   │
│   ├── utils/                         # Utilities
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuration management
│   │   ├── logger.py                  # Logging utilities
│   │   └── statistics.py              # Game statistics
│   │
│   └── assets/                        # From pyker
│       ├── cards/                     # 52 card PNG files
│       │   ├── 2C.png → AS.png
│       │   └── back_red.png
│       ├── buttons/                   # Action button images
│       │   ├── bet.png
│       │   ├── call.png
│       │   ├── check.png
│       │   ├── fold.png
│       │   └── raise.png
│       ├── fonts/                     # Pixel fonts
│       │   └── PixeloidMono-1G8ae.ttf
│       └── others/                    # Misc assets
│           ├── dealer.png
│           └── bet.png
│
├── texasholdem/                       # Cloned texasholdem repo
│   └── [texasholdem source code]
│
├── pyker/                             # Cloned pyker repo (for reference)
│   └── [pyker source code]
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_engine/
│   │   ├── test_game_wrapper.py
│   │   └── test_state_manager.py
│   ├── test_gui/
│   │   ├── test_card_renderer.py
│   │   └── test_event_handler.py
│   └── test_agents/
│       ├── test_agent_manager.py
│       └── test_gto_agent.py
│
├── examples/                          # Example scripts
│   ├── simple_game.py
│   ├── ai_tournament.py
│   ├── replay_viewer.py
│   └── training_example.py
│
└── docs/                              # Documentation
    ├── index.md
    ├── getting_started.md
    ├── architecture.md
    ├── api_reference.md
    └── ai_development.md
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Basic game running with Pygame GUI

**Tasks:**
- [ ] Setup project structure
- [ ] Install dependencies (texasholdem, pygame)
- [ ] Create `PokerGame` wrapper class
- [ ] Implement `CardRenderer`
- [ ] Basic `PygameGUI` with table rendering
- [ ] Asset loading from pyker
- [ ] Basic event handling
- [ ] Simple game loop

**Deliverable:** Can play a hand with UI (human vs random AI)

### Phase 2: Full GUI (Week 2-3)
**Goal:** Complete visual experience

**Tasks:**
- [ ] Player rendering around table
- [ ] Community card display
- [ ] Pot and bet display
- [ ] Action button UI
- [ ] Raise amount input
- [ ] Current player indicator
- [ ] Game phase indicator
- [ ] Card dealing animation
- [ ] Chip movement animation
- [ ] Status messages (folded, all-in, etc.)

**Deliverable:** Full visual poker game with animations

### Phase 3: AI Integration (Week 3-4)
**Goal:** Multiple AI skill levels

**Tasks:**
- [ ] Create `AgentManager`
- [ ] Integrate texasholdem agents (random, call)
- [ ] Implement GTO agent
- [ ] Preflop hand strength calculator
- [ ] Pot odds calculator
- [ ] Agent evaluation framework
- [ ] AI vs AI simulation mode

**Deliverable:** Play against sophisticated AI opponents

### Phase 4: Advanced Features (Week 4-5)
**Goal:** Production-quality application

**Tasks:**
- [ ] Game history export/import
- [ ] Visual replay viewer
- [ ] Statistics tracking
- [ ] Configuration system
- [ ] Multiple table support
- [ ] Tournament mode
- [ ] Settings menu
- [ ] Save/load game state

**Deliverable:** Complete poker application

### Phase 5: ML Integration (Week 5-6)
**Goal:** Machine learning AI

**Tasks:**
- [ ] Reinforcement learning agent framework
- [ ] Training infrastructure
- [ ] Neural network architecture
- [ ] Experience replay
- [ ] Model saving/loading
- [ ] Training visualization
- [ ] Agent comparison tools

**Deliverable:** ML-powered poker AI

### Phase 6: Polish & Release (Week 6-7)
**Goal:** Production release

**Tasks:**
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation
- [ ] Code cleanup
- [ ] Package for distribution
- [ ] CI/CD setup
- [ ] Release v1.0

**Deliverable:** Production-ready poker.ev v1.0

---

## Code Examples

### Example 1: Simple Game
```python
# examples/simple_game.py
from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.gui.pygame_gui import PygameGUI
from poker_ev.agents.agent_manager import AgentManager

# Create game
game = PokerGame(num_players=3, buyin=1000, big_blind=10, small_blind=5)

# Setup agents
agents = AgentManager()
agents.register_agent(1, AgentManager.random_agent)
agents.register_agent(2, AgentManager.call_agent)

# Create and run GUI
gui = PygameGUI(game, agents)
gui.run()
```

### Example 2: AI Tournament
```python
# examples/ai_tournament.py
from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.agents.agent_manager import AgentManager
from poker_ev.agents.advanced import GTOAgent

def run_tournament(num_games=100):
    """Run a tournament between different AI agents"""

    results = {
        'random': 0,
        'call': 0,
        'gto': 0
    }

    for _ in range(num_games):
        game = PokerGame(num_players=3, buyin=1000)

        agents = AgentManager()
        gto = GTOAgent()

        agents.register_agent(0, AgentManager.random_agent)
        agents.register_agent(1, AgentManager.call_agent)
        agents.register_agent(2, gto.get_action)

        # Run game to completion
        while game.is_game_running():
            if not game.is_hand_running():
                game.start_new_hand()

            current = game.engine.current_player
            action, amount = agents.get_action(game.engine, current)
            game.take_action(action, amount)

        # Record winner
        # ... update results

    print(results)

if __name__ == "__main__":
    run_tournament()
```

### Example 3: Replay Viewer
```python
# examples/replay_viewer.py
from poker_ev.gui.pygame_gui import PygameGUI
from texasholdem import TexasHoldEm

def replay_game(pgn_file: str):
    """Replay a saved game visually"""

    # Load game from PGN
    game = TexasHoldEm.import_history(pgn_file)

    # Create replay GUI
    gui = PygameGUI(game, replay_mode=True)
    gui.run_replay()

if __name__ == "__main__":
    replay_game("./games/epic_hand.pgn")
```

---

## Technical Challenges

### Challenge 1: Card Format Mismatch
**Problem:** texasholdem uses integer card representation, pyker uses object-based

**Solution:** `CardRenderer` class translates between formats
```python
# texasholdem Card → pyker sprite name
card = Card("Kd")  # texasholdem
sprite_name = card_renderer.card_to_sprite_name(card)  # "KD"
sprite = card_sprites[sprite_name]  # pygame.Surface
```

### Challenge 2: Event Loop Integration
**Problem:** texasholdem is synchronous, Pygame is event-driven

**Solution:** Wrap texasholdem in async-friendly interface
```python
# Non-blocking action execution
if current_player == 0:  # Human
    # Wait for GUI input
    action = await gui.get_player_action()
else:  # AI
    # Get AI action (fast)
    action = agent_manager.get_action(game, current_player)

game.take_action(action)
```

### Challenge 3: State Synchronization
**Problem:** Keep GUI in sync with game engine state

**Solution:** Observer pattern with state updates
```python
class PokerGame:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def take_action(self, action, amount=0):
        self.engine.take_action(action, total=amount)
        # Notify all observers
        self.notify_observers()

    def notify_observers(self):
        state = self.get_game_state()
        for observer in self.observers:
            observer.on_state_change(state)
```

### Challenge 4: Performance with Animations
**Problem:** Smooth 60 FPS while running game logic

**Solution:** Separate render thread and game thread
```python
# Render loop (60 FPS)
while running:
    for event in pygame.event.get():
        handle_event(event)

    render()  # Fast
    clock.tick(60)

# Game logic (separate, as needed)
if action_ready:
    execute_action()  # Fast (texasholdem is optimized)
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_engine/test_game_wrapper.py
def test_game_initialization():
    game = PokerGame(num_players=6, buyin=1000)
    assert game.num_players == 6
    assert game.engine.buyin == 1000

def test_get_game_state():
    game = PokerGame(num_players=3)
    game.start_new_hand()
    state = game.get_game_state()

    assert 'current_player' in state
    assert 'board' in state
    assert 'pot' in state
    assert len(state['players']) == 3
```

### Integration Tests
```python
# tests/test_gui/test_pygame_integration.py
def test_render_without_crash():
    """Test that GUI can render without crashing"""
    game = PokerGame(num_players=2)
    gui = PygameGUI(game)

    # Render one frame
    gui.render()
    # Should not crash
```

### AI Tests
```python
# tests/test_agents/test_gto_agent.py
def test_gto_agent_returns_valid_actions():
    game = PokerGame(num_players=2)
    game.start_new_hand()

    gto = GTOAgent()
    action, amount = gto.get_action(game.engine)

    # Verify action is valid
    assert game.engine.valid_action(game.engine.current_player, action)
```

---

## Deployment Plan

### Requirements
```txt
# requirements.txt
texasholdem>=0.11.0
pygame>=2.1.2
numpy>=1.24.0
# For ML agents
torch>=2.0.0
# For testing
pytest>=7.2.0
pytest-cov>=4.0.0
black>=23.0.0
```

### Package Setup
```toml
# pyproject.toml
[tool.poetry]
name = "poker-ev"
version = "1.0.0"
description = "AI Poker Application with Advanced Agents"
authors = ["Your Name <your.email@example.com>"]
license = "MIT"

[tool.poetry.dependencies]
python = "^3.8"
texasholdem = "^0.11.0"
pygame = "^2.1.2"

[tool.poetry.scripts]
poker-ev = "poker_ev.main:main"
```

### Installation
```bash
# From PyPI (future)
pip install poker-ev

# From source
git clone https://github.com/yourusername/poker.ev
cd poker.ev
pip install -e .

# Run
poker-ev
```

---

## Success Metrics

### Phase 1 Success Criteria
- ✅ Game runs without crashes
- ✅ Cards display correctly
- ✅ Basic actions work (fold, call, check)
- ✅ Game state updates properly

### Phase 2 Success Criteria
- ✅ All 6 players visible
- ✅ Animations smooth (60 FPS)
- ✅ All action buttons functional
- ✅ Pot and bets display correctly

### Phase 3 Success Criteria
- ✅ GTO agent makes reasonable decisions
- ✅ GTO agent beats random agent 70%+ of time
- ✅ Multiple agents can play simultaneously

### Final Release Criteria
- ✅ 90%+ test coverage
- ✅ Comprehensive documentation
- ✅ No known bugs
- ✅ Performance: 60 FPS sustained
- ✅ ML agent shows learning curve
- ✅ Can export/import game history

---

## Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| Phase 1 | Week 1-2 | Basic playable game |
| Phase 2 | Week 2-3 | Full visual experience |
| Phase 3 | Week 3-4 | AI opponents |
| Phase 4 | Week 4-5 | Advanced features |
| Phase 5 | Week 5-6 | ML integration |
| Phase 6 | Week 6-7 | Production release |

**Total:** ~7 weeks to v1.0 release

---

## Next Steps

1. **Immediate (Today):**
   - ✅ Clone texasholdem repository
   - ✅ Create integration plan
   - [ ] Setup project structure
   - [ ] Install dependencies

2. **This Week:**
   - [ ] Implement `PokerGame` wrapper
   - [ ] Implement `CardRenderer`
   - [ ] Create basic `PygameGUI`
   - [ ] Load assets from pyker

3. **Next Week:**
   - [ ] Complete GUI rendering
   - [ ] Add animations
   - [ ] Implement event handling
   - [ ] Play first complete hand!

---

## Conclusion

This integration plan provides a **clear roadmap** to combine:
- **texasholdem's** production-grade game engine (fast, tested, reliable)
- **pyker's** beautiful visual assets (cards, buttons, fonts)

The result: **poker.ev** - a professional AI poker application suitable for:
- AI research and development
- Poker strategy learning
- Casual play with sophisticated opponents
- Machine learning experimentation

**Key Advantages:**
1. ✅ Rock-solid foundation (texasholdem's 6,626 lines of tested code)
2. ✅ Beautiful UX (pyker's retro aesthetic)
3. ✅ Extensible AI framework (easy to add new agents)
4. ✅ Production-quality (proper testing, documentation, distribution)

**Let's build it!** 🚀
