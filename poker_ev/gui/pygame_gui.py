"""
Main Pygame GUI for poker.ev
"""

import pygame
import os
from pathlib import Path
from texasholdem import ActionType, HandPhase
from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.gui.card_renderer import CardRenderer
from poker_ev.gui.event_handler import EventHandler
from poker_ev.agents.agent_manager import AgentManager
from typing import Optional
import math
import threading

# Chat components
from poker_ev.gui.chat.chat_panel import ChatPanel
from poker_ev.llm.poker_advisor import PokerAdvisor
from poker_ev.llm.game_context import GameContextProvider


class PygameGUI:
    """
    Main Pygame GUI for poker.ev

    This class handles all rendering, animations, and user interaction
    for the poker game.
    """

    # Colors
    TABLE_GREEN = (53, 101, 77)
    TABLE_BORDER = (34, 80, 57)
    BORDER_COLOR = (200, 200, 200)
    BG_COLOR = (20, 20, 20)
    TEXT_COLOR = (255, 255, 255)
    GOLD_COLOR = (255, 215, 0)
    RED_COLOR = (255, 100, 100)
    BUTTON_BG = (40, 40, 40)
    BUTTON_HOVER = (60, 60, 60)

    def __init__(self, game: PokerGame, agent_manager: AgentManager,
                 window_size: tuple = (1400, 900), enable_chat: bool = True,
                 enable_hand_history: bool = True):
        """
        Initialize the Pygame GUI

        Args:
            game: PokerGame instance
            agent_manager: AgentManager for AI players
            window_size: (width, height) of the window
            enable_chat: Enable AI poker advisor chat panel
            enable_hand_history: Enable automatic hand saving to Pinecone (default: True)
        """
        pygame.init()

        self.game = game
        self.agent_manager = agent_manager
        self.window_size = window_size
        self.enable_chat = enable_chat

        # Create window
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Poker.ev - AI Poker Application + Advisor")

        # Load assets
        self.load_assets()

        # Initialize components
        self.card_renderer = CardRenderer(self.card_sprites)
        self.event_handler = EventHandler(self)

        # GUI state
        self.showing_raise_input = False
        self.raise_amount = 0
        self.raise_percentage = 0.0
        self.game_over = False
        self.final_game_state = None

        # Animation state
        self.message = ""
        self.message_timer = 0

        # Chat panel (if enabled)
        self.chat_panel = None
        self.poker_advisor = None
        self.chat_visible = True  # Chat panel visibility toggle
        if self.enable_chat:
            self._init_chat_panel()

        # Player position on table (positions around ellipse)
        self.player_positions = self._calculate_player_positions()

        # Hand history tracking (if enabled)
        self.enable_hand_history = enable_hand_history
        self.hand_history = None
        self.current_hand_id = None
        self.hand_start_state = None
        self.player_starting_chips = {}
        self._last_hand_active_state = None  # Track state changes

        if self.enable_hand_history:
            self._init_hand_history()

    def _init_chat_panel(self):
        """Initialize the AI poker advisor chat panel"""
        # Calculate chat panel position (right side)
        chat_width = 400
        chat_panel_rect = pygame.Rect(
            self.window_size[0] - chat_width,
            0,
            chat_width,
            self.window_size[1]
        )

        # Create chat panel with FindersKeepers retro fonts
        self.chat_panel = ChatPanel(
            panel_rect=chat_panel_rect,
            font_small=self.chat_font_small,
            font_medium=self.chat_font_medium,
            font_large=self.chat_font_large,
            on_message_send=self._handle_chat_message
        )

        # Initialize poker advisor
        try:
            game_context = GameContextProvider(self.game)
            self.poker_advisor = PokerAdvisor(
                game_context_provider=game_context
            )
            self.set_message("Poker Advisor Ready! Press Tab to toggle panel")
        except Exception as e:
            self.set_message(f"Chat unavailable: {str(e)}")
            self.enable_chat = False

    def _handle_chat_message(self, message: str):
        """
        Handle user chat message with streaming response

        Args:
            message: User's message
        """
        if not self.poker_advisor:
            self.chat_panel.add_ai_response("Poker advisor not available.")
            return

        # Get current game state
        game_state = self.game.get_game_state()

        # Run in thread to avoid blocking game
        def stream_response():
            try:
                # Set typing indicator
                self.chat_panel.set_typing(True)

                # Collect full response while streaming
                full_response = ""
                for chunk in self.poker_advisor.get_advice_stream(message, game_state):
                    full_response += chunk

                # Add complete response to chat
                self.chat_panel.add_ai_response(full_response)

            except Exception as e:
                self.chat_panel.add_ai_response(f"Error: {str(e)}")

        thread = threading.Thread(target=stream_response, daemon=True)
        thread.start()

    def _init_hand_history(self):
        """Initialize hand history for Pinecone storage"""
        try:
            from poker_ev.memory.hand_history import HandHistory
            self.hand_history = HandHistory()
            print("✅ Hand history initialized - hands will be saved to Pinecone")
        except Exception as e:
            print(f"⚠️  Hand history unavailable: {e}")
            print("   Hands will not be saved. Set PINECONE_API_KEY in .env to enable.")
            self.enable_hand_history = False
            self.hand_history = None

    def _format_card(self, card_obj) -> str:
        """Format a card object to readable string"""
        rank_map = {
            0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7', 6: '8',
            7: '9', 8: 'T', 9: 'J', 10: 'Q', 11: 'K', 12: 'A'
        }
        suit_map = {1: '♠', 2: '♥', 4: '♦', 8: '♣'}

        if hasattr(card_obj, 'rank') and hasattr(card_obj, 'suit'):
            return f"{rank_map.get(card_obj.rank, '?')}{suit_map.get(card_obj.suit, '?')}"
        return str(card_obj)

    def _track_hand_start(self, state: dict):
        """Track when a new hand starts"""
        if not self.enable_hand_history or not self.hand_history:
            return

        # Only track if hand is active and we haven't tracked this hand yet
        if state['hand_active'] and self.current_hand_id is None:
            import time
            from datetime import datetime

            self.current_hand_id = f"hand_{int(time.time())}"
            self.hand_start_state = state.copy()

            # Save starting chips for profit calculation
            self.player_starting_chips = {
                i: p['chips'] for i, p in enumerate(state['players'])
            }

            print(f"\n📋 Hand started: {self.current_hand_id}")

    def _track_hand_end(self, state: dict):
        """Track when a hand ends and save to Pinecone"""
        if not self.enable_hand_history or not self.hand_history:
            return

        # Debug: Log state transitions
        current_active = state['hand_active']
        if self._last_hand_active_state is not None and self._last_hand_active_state != current_active:
            print(f"🔄 Hand state transition: {self._last_hand_active_state} -> {current_active}")
        self._last_hand_active_state = current_active

        # Hand ended if it was active and now isn't, and we have a tracked hand
        if not state['hand_active'] and self.current_hand_id is not None:
            from datetime import datetime

            print(f"\n🏁 Hand ended: {self.current_hand_id}")
            print(f"💾 Saving hand to Pinecone...")

            # Prepare hand data
            hand_data = self._prepare_hand_data(state)

            # Log what we're saving
            print(f"   Cards: {', '.join(hand_data['your_cards']) if hand_data['your_cards'] else 'None'}")
            print(f"   Board: {', '.join(hand_data['board']) if hand_data['board'] else 'None'}")
            print(f"   Outcome: {hand_data['outcome']}")
            print(f"   Profit: ${hand_data['profit']:+d}")

            # Save to Pinecone
            try:
                success = self.hand_history.save_hand(hand_data)
                if success:
                    print(f"✅ Hand saved successfully!")
                else:
                    print(f"⚠️  Failed to save hand")
            except Exception as e:
                print(f"❌ Error saving hand: {e}")
                import traceback
                traceback.print_exc()

            # Reset hand tracking
            self.current_hand_id = None
            self.hand_start_state = None

    def _prepare_hand_data(self, end_state: dict) -> dict:
        """Prepare hand data for Pinecone storage"""
        from datetime import datetime
        import time

        start_state = self.hand_start_state or {}

        # Get player 0 data
        player_0_start = start_state.get('players', [{}])[0]
        player_0_end = end_state.get('players', [{}])[0]

        # Format cards
        your_cards = []
        if player_0_start.get('hand'):
            your_cards = [self._format_card(c) for c in player_0_start['hand']]

        board_cards = []
        if end_state.get('board'):
            board_cards = [self._format_card(c) for c in end_state['board']]

        # Calculate profit
        start_chips = self.player_starting_chips.get(0, 1000)
        end_chips = player_0_end.get('chips', start_chips)
        profit = end_chips - start_chips

        # Determine outcome
        outcome = 'unknown'
        if player_0_end.get('folded'):
            outcome = 'folded'
        elif profit > 0:
            outcome = 'won'
        elif profit < 0:
            outcome = 'lost'
        else:
            outcome = 'push'

        # Build hand data
        hand_data = {
            'hand_id': self.current_hand_id,
            'timestamp': datetime.now().isoformat(),
            'your_cards': your_cards,
            'board': board_cards,
            'pot': end_state.get('pot', 0),
            'phase': str(end_state.get('hand_phase', 'unknown')),
            'position': 'Button',  # Simplified - could be enhanced
            'outcome': outcome,
            'profit': profit,
            'actions_summary': f"Hand completed at {datetime.now().strftime('%H:%M:%S')}",
            'notes': f"Poker.ev game hand"
        }

        return hand_data

    def load_assets(self):
        """Load all assets from pyker"""
        assets_dir = "poker_ev/assets"
        cards_dir = Path(os.path.join(assets_dir, "cards"))
        buttons_dir = Path(os.path.join(assets_dir, "buttons"))
        fonts_dir = Path(os.path.join(assets_dir, "fonts"))

        # Load card sprites
        self.card_sprites = {}
        if cards_dir.exists():
            for filename in os.listdir(cards_dir):
                if filename.endswith('.png'):
                    card_name = filename[:-4]  # Remove .png
                    card_sprite = pygame.image.load(os.path.join(cards_dir, filename))
                    # Scale cards to reasonable size
                    card_sprite = pygame.transform.scale(card_sprite,
                        (int(card_sprite.get_width() * 2), int(card_sprite.get_height() * 2)))
                    self.card_sprites[card_name] = card_sprite

        # Load button sprites
        self.button_sprites = {}
        if buttons_dir.exists():
            for filename in os.listdir(buttons_dir):
                if filename.endswith('.png'):
                    button_name = filename[:-4]
                    button_sprite = pygame.image.load(os.path.join(buttons_dir, filename))
                    button_sprite = pygame.transform.scale(button_sprite,
                        (int(button_sprite.get_width() * 3), int(button_sprite.get_height() * 3)))
                    self.button_sprites[button_name] = button_sprite

        # Load fonts
        pygame.font.init()

        # Main game UI fonts (Pixeloid)
        font_path = os.path.join(fonts_dir, "PixeloidMono-1G8ae.ttf")
        if os.path.exists(font_path):
            self.font_small = pygame.font.Font(font_path, 14)
            self.font_medium = pygame.font.Font(font_path, 20)
            self.font_large = pygame.font.Font(font_path, 32)
        else:
            # Fallback to default font
            self.font_small = pygame.font.Font(None, 20)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_large = pygame.font.Font(None, 42)

        # Chat UI fonts (FindersKeepers - Geneva recreation, scaled up for readability)
        finders_path = os.path.join(fonts_dir, "FindersKeepers.ttf")
        if os.path.exists(finders_path):
            self.chat_font_small = pygame.font.Font(finders_path, 20)
            self.chat_font_medium = pygame.font.Font(finders_path, 24)
            self.chat_font_large = pygame.font.Font(finders_path, 32)
        else:
            # Fallback to Pixeloid for chat
            if os.path.exists(font_path):
                self.chat_font_small = pygame.font.Font(font_path, 20)
                self.chat_font_medium = pygame.font.Font(font_path, 24)
                self.chat_font_large = pygame.font.Font(font_path, 32)
            else:
                # Final fallback
                self.chat_font_small = pygame.font.Font(None, 20)
                self.chat_font_medium = pygame.font.Font(None, 24)
                self.chat_font_large = pygame.font.Font(None, 32)

    def _calculate_player_positions(self):
        """Calculate positions for players around the table"""
        positions = []
        center_x, center_y = self.window_size[0] // 2, self.window_size[1] // 2

        # Ellipse parameters
        rx = 450  # horizontal radius
        ry = 280  # vertical radius

        # Position players around ellipse
        for i in range(self.game.num_players):
            angle = (i / self.game.num_players) * 2 * math.pi - (math.pi / 2)  # Start from top
            x = center_x + rx * math.cos(angle)
            y = center_y + ry * math.sin(angle)
            positions.append((int(x), int(y)))

        return positions

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True

        while running:
            # Get current game state (needed for both normal flow and game over screen)
            state = self.game.get_game_state()

            # Continuously capture state during active hands (for game over screen)
            if state['hand_active']:
                self.final_game_state = state

            # Track hand lifecycle for Pinecone storage
            # IMPORTANT: Check for hand end BEFORE starting new hand
            self._track_hand_end(state)

            # Check if player is busted
            if not self.game_over and self.game.is_player_busted():
                self.game_over = True
                # final_game_state already contains last active state with visible cards
                self.set_message("Game Over - You're out of chips!", duration=9999)

            # If game over, just show the game over screen
            if self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # Restart the game
                            self.reset_game()

                self.render_game_over()
                pygame.display.flip()
                clock.tick(60)
                continue

            # Normal game flow
            if not self.game.is_game_running():
                break

            # Start new hand if needed
            if not self.game.is_hand_running():
                self.game.start_new_hand()
                self.set_message("New hand dealt!")
                # Get updated state after starting new hand
                state = self.game.get_game_state()

            # Track hand start (for new hands)
            self._track_hand_start(state)
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    # Handle chat events first (if chat is visible, it takes priority)
                    if self.chat_panel and self.chat_visible:
                        handled = self.chat_panel.handle_event(event)
                        if not handled:
                            self.event_handler.handle_event(event)
                    else:
                        self.event_handler.handle_event(event)

            # Process AI players
            if state['hand_active'] and state['current_player'] is not None:
                current = state['current_player']

                # Check if current player is AI
                if self.agent_manager.has_agent(current):
                    # Small delay for AI (so humans can see what's happening)
                    pygame.time.wait(500)

                    # Get AI action
                    action, amount = self.agent_manager.get_action(self.game.engine, current)

                    # Execute action
                    self.game.take_action(action, amount)

                    # Show message
                    action_str = self._action_to_string(action, amount)
                    self.set_message(f"Player {current}: {action_str}")

            # Clear button registrations and render current frame
            self.event_handler.clear_buttons()
            self.render(state)

            # Update chat panel (only if visible)
            if self.chat_panel and self.chat_visible:
                self.chat_panel.update()
                self.chat_panel.render(self.screen)

            # Update display
            pygame.display.flip()
            clock.tick(60)  # 60 FPS

            # Update message timer
            if self.message_timer > 0:
                self.message_timer -= 1
                if self.message_timer == 0:
                    self.message = ""

        pygame.quit()

    def render(self, state: dict):
        """Render the current game state"""
        self.screen.fill(self.BG_COLOR)

        # Draw table
        self.render_table()

        # Draw community cards
        if state['hand_active']:
            self.render_community_cards(state['board'])

        # Draw pot
        self.render_pot(state['pot'])

        # Draw players
        self.render_players(state['players'], state.get('current_player'))

        # Draw phase indicator
        if state['hand_active']:
            self.render_phase(state['hand_phase'])

        # Draw action buttons for human player (player 0)
        if state['hand_active'] and state['current_player'] == 0:
            if not self.showing_raise_input:
                self.render_action_buttons(state['valid_actions'])
            else:
                self.render_raise_input(state['chips_to_call'], state['min_raise'])

        # Draw message
        if self.message:
            self.render_message()

    def render_table(self):
        """Draw the poker table"""
        center_x, center_y = self.window_size[0] // 2, self.window_size[1] // 2

        # Outer ellipse (border)
        table_rect = pygame.Rect(center_x - 480, center_y - 300, 960, 600)
        pygame.draw.ellipse(self.screen, self.TABLE_BORDER, table_rect)

        # Inner ellipse (table surface)
        table_rect_inner = pygame.Rect(center_x - 470, center_y - 290, 940, 580)
        pygame.draw.ellipse(self.screen, self.TABLE_GREEN, table_rect_inner)

        # Table border
        pygame.draw.ellipse(self.screen, self.BORDER_COLOR, table_rect, 3)

    def render_community_cards(self, board: list):
        """Render community cards in the center"""
        if not board:
            return

        center_x = self.window_size[0] // 2
        center_y = self.window_size[1] // 2

        card_width = 100
        card_spacing = 110
        start_x = center_x - ((len(board) * card_spacing) // 2)

        for i, card in enumerate(board):
            x = start_x + i * card_spacing
            y = center_y - 60
            sprite = self.card_renderer.get_card_sprite(card, scale=(card_width, 140))
            if sprite:
                self.screen.blit(sprite, (x, y))

    def render_pot(self, pot_amount: int):
        """Render pot amount"""
        center_x, center_y = self.window_size[0] // 2, self.window_size[1] // 2

        text = self.font_large.render(f"Pot: ${pot_amount}", True, self.GOLD_COLOR)
        text_rect = text.get_rect(center=(center_x, center_y + 120))
        self.screen.blit(text, text_rect)

    def render_players(self, players: list, current_player: Optional[int]):
        """Render all players around the table"""
        for i, player in enumerate(players):
            if not player.get('in_game'):
                continue

            x, y = self.player_positions[i]
            is_current = (i == current_player)
            is_human = (i == 0)
            self.render_player(player, x, y, is_human, is_current)

    def render_player(self, player: dict, x: int, y: int, is_human: bool, is_current: bool):
        """Render a single player"""
        # Player box
        box_width, box_height = 180, 140
        box_rect = pygame.Rect(x - box_width//2, y - box_height//2, box_width, box_height)

        # Highlight current player
        if is_current:
            pygame.draw.rect(self.screen, self.GOLD_COLOR, box_rect.inflate(8, 8), 3)

        pygame.draw.rect(self.screen, self.BUTTON_BG, box_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, box_rect, 2)

        # Player name
        name = "You" if is_human else f"Player {player['id']}"
        name_text = self.font_medium.render(name, True, self.TEXT_COLOR)
        self.screen.blit(name_text, (x - box_width//2 + 10, y - box_height//2 + 10))

        # Chips
        chips_text = self.font_small.render(f"${player['chips']}", True, self.GOLD_COLOR)
        self.screen.blit(chips_text, (x - box_width//2 + 10, y - box_height//2 + 35))

        # Current bet
        if player.get('bet', 0) > 0:
            bet_text = self.font_small.render(f"Bet: ${player['bet']}", True, self.RED_COLOR)
            self.screen.blit(bet_text, (x - box_width//2 + 10, y - box_height//2 + 55))

        # Cards
        if player.get('active') and 'hand' in player and len(player['hand']) > 0:
            card_y = y - box_height//2 + 80
            for i, card in enumerate(player['hand']):
                card_x = x - box_width//2 + 10 + i * 70
                if is_human:
                    # Show cards for human
                    sprite = self.card_renderer.get_card_sprite(card, scale=(60, 84))
                else:
                    # Show card back for AI
                    sprite = self.card_renderer.get_card_back(scale=(60, 84))
                if sprite:
                    self.screen.blit(sprite, (card_x, card_y))

        # Status
        if player.get('folded'):
            status_text = self.font_medium.render("FOLDED", True, self.RED_COLOR)
            self.screen.blit(status_text, (x - 40, y + box_height//2 + 10))
        elif player.get('all_in'):
            status_text = self.font_medium.render("ALL IN", True, self.GOLD_COLOR)
            self.screen.blit(status_text, (x - 40, y + box_height//2 + 10))

    def render_phase(self, phase: HandPhase):
        """Render the current hand phase"""
        phase_str = str(phase).replace("HandPhase.", "")
        text = self.font_medium.render(phase_str, True, self.TEXT_COLOR)
        text_rect = text.get_rect(center=(self.window_size[0] // 2, 50))
        self.screen.blit(text, text_rect)

    def render_action_buttons(self, valid_actions: list):
        """Render action buttons for human player"""
        button_y = self.window_size[1] - 100
        button_spacing = 150
        num_buttons = len(valid_actions)
        start_x = (self.window_size[0] - (num_buttons * button_spacing)) // 2

        action_button_names = {
            ActionType.FOLD: 'fold',
            ActionType.CHECK: 'check',
            ActionType.CALL: 'call',
            ActionType.RAISE: 'raise',
            ActionType.ALL_IN: 'allin',
        }

        for i, action in enumerate(valid_actions):
            x = start_x + i * button_spacing

            # Get button sprite
            button_name = action_button_names.get(action, 'unknown')
            if button_name in self.button_sprites:
                sprite = self.button_sprites[button_name]
                self.screen.blit(sprite, (x, button_y))

                # Register for click detection
                button_rect = pygame.Rect(x, button_y, sprite.get_width(), sprite.get_height())
                self.event_handler.register_button(action, button_rect)
            else:
                # Fallback: draw text button
                button_rect = pygame.Rect(x, button_y, 120, 50)
                pygame.draw.rect(self.screen, self.BUTTON_BG, button_rect)
                pygame.draw.rect(self.screen, self.BORDER_COLOR, button_rect, 2)

                text = self.font_medium.render(button_name.upper(), True, self.TEXT_COLOR)
                text_rect = text.get_rect(center=button_rect.center)
                self.screen.blit(text, text_rect)

                self.event_handler.register_button(action, button_rect)

    def render_raise_input(self, chips_to_call: int, min_raise: int):
        """Render raise amount input"""
        print(f"[DEBUG] render_raise_input called - min_raise={min_raise}, percentage={self.raise_percentage:.2f}")
        center_x = self.window_size[0] // 2
        center_y = self.window_size[1] // 2

        # Background panel
        panel_rect = pygame.Rect(center_x - 250, center_y + 150, 500, 150)
        pygame.draw.rect(self.screen, self.BUTTON_BG, panel_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, panel_rect, 3)

        # Title
        title = self.font_large.render("Raise Amount", True, self.TEXT_COLOR)
        self.screen.blit(title, (center_x - 120, center_y + 160))

        # Calculate raise amount based on percentage
        player = self.game.engine.players[0]
        # The total bet ranges from (chips_to_call + min_raise) to (chips_to_call + player.chips)
        min_total_bet = chips_to_call + min_raise
        max_total_bet = chips_to_call + player.chips
        self.raise_amount = int(min_total_bet + (max_total_bet - min_total_bet) * self.raise_percentage)

        # Amount display
        amount_text = self.font_medium.render(f"${self.raise_amount}", True, self.GOLD_COLOR)
        self.screen.blit(amount_text, (center_x - 40, center_y + 200))

        # Slider
        slider_rect = pygame.Rect(center_x - 200, center_y + 240, 400, 20)
        pygame.draw.rect(self.screen, (100, 100, 100), slider_rect)

        # Slider fill
        fill_width = int(400 * self.raise_percentage)
        fill_rect = pygame.Rect(center_x - 200, center_y + 240, fill_width, 20)
        pygame.draw.rect(self.screen, self.GOLD_COLOR, fill_rect)

        self.event_handler.register_raise_slider(slider_rect)

        # Confirm button
        confirm_rect = pygame.Rect(center_x - 60, center_y + 270, 120, 40)
        pygame.draw.rect(self.screen, (0, 150, 0), confirm_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, confirm_rect, 2)

        confirm_text = self.font_medium.render("Confirm", True, self.TEXT_COLOR)
        text_rect = confirm_text.get_rect(center=confirm_rect.center)
        self.screen.blit(confirm_text, text_rect)

        self.event_handler.register_raise_confirm(confirm_rect)

        print(f"[DEBUG] Slider registered: {slider_rect}, Confirm registered: {confirm_rect}, raise_amount=${self.raise_amount}")

    def render_message(self):
        """Render status message"""
        text = self.font_large.render(self.message, True, self.GOLD_COLOR)
        text_rect = text.get_rect(center=(self.window_size[0] // 2, self.window_size[1] - 50))

        # Background for better visibility
        bg_rect = text_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(self.screen, self.GOLD_COLOR, bg_rect, 2)

        self.screen.blit(text, text_rect)

    def render_game_over(self):
        """Render game over screen - overlays game over image on final game state"""
        # Render the final game state as background
        if self.final_game_state:
            self.render(self.final_game_state)
        else:
            # Fallback if no final state captured
            self.screen.fill(self.BG_COLOR)

        # Create semi-transparent overlay
        overlay = pygame.Surface(self.window_size)
        overlay.set_alpha(128)  # 50% transparency
        overlay.fill((0, 0, 0))  # Black overlay
        self.screen.blit(overlay, (0, 0))

        # Center coordinates
        center_x = self.window_size[0] // 2
        center_y = self.window_size[1] // 2

        # Display game over image scaled to 2x size
        gameover_bottom_y = center_y  # Track bottom of game over element
        if 'gameover' in self.button_sprites:
            # Load the original image and scale to 2x
            assets_dir = "poker_ev/assets"
            gameover_path = os.path.join(assets_dir, "buttons", "gameover.png")
            if os.path.exists(gameover_path):
                gameover_original = pygame.image.load(gameover_path)
                # Scale to 2x size
                gameover_sprite = pygame.transform.scale(gameover_original,
                    (int(gameover_original.get_width() * 2), int(gameover_original.get_height() * 2)))
                sprite_rect = gameover_sprite.get_rect(center=(center_x, center_y))
                self.screen.blit(gameover_sprite, sprite_rect)
                gameover_bottom_y = sprite_rect.bottom
            else:
                # Fallback to pre-loaded sprite (which has 3x scaling from load_assets)
                gameover_sprite = self.button_sprites['gameover']
                sprite_rect = gameover_sprite.get_rect(center=(center_x, center_y))
                self.screen.blit(gameover_sprite, sprite_rect)
                gameover_bottom_y = sprite_rect.bottom
        else:
            # Fallback text if image not found
            title_text = self.font_large.render("GAME OVER", True, self.RED_COLOR)
            title_rect = title_text.get_rect(center=(center_x, center_y))
            self.screen.blit(title_text, title_rect)
            gameover_bottom_y = title_rect.bottom

        # Display "R to Restart" text directly under game over image
        restart_text = self.font_large.render("R to Restart", True, self.GOLD_COLOR)
        restart_rect = restart_text.get_rect(center=(center_x, gameover_bottom_y + 60))

        # Add background for better visibility
        bg_rect = restart_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), bg_rect)
        pygame.draw.rect(self.screen, self.GOLD_COLOR, bg_rect, 3)

        self.screen.blit(restart_text, restart_rect)

    # ==================== Action Handlers ====================

    def handle_action_click(self, action: ActionType):
        """Handle action button click from user"""
        if action == ActionType.RAISE:
            # Show raise input
            print("[DEBUG] RAISE button clicked - showing raise UI")
            self.showing_raise_input = True
            self.raise_percentage = 0.0
        else:
            # Execute action immediately
            state = self.game.get_game_state()
            amount = 0
            if action == ActionType.CALL:
                amount = state['chips_to_call']

            success = self.game.take_action(action, amount)

            if success:
                action_str = self._action_to_string(action, amount)
                self.set_message(f"You: {action_str}")

    def confirm_raise(self):
        """Confirm raise amount and execute"""
        print(f"[DEBUG] confirm_raise called - raise_amount=${self.raise_amount}")
        self.showing_raise_input = False
        success = self.game.take_action(ActionType.RAISE, self.raise_amount)

        print(f"[DEBUG] Raise action success={success}")
        if success:
            self.set_message(f"You: Raise to ${self.raise_amount}")

    def cancel_raise(self):
        """Cancel raise input"""
        self.showing_raise_input = False

    def update_raise_amount(self, percentage: float):
        """Update raise amount from slider"""
        print(f"[DEBUG] update_raise_amount called - percentage={percentage:.2f}")
        self.raise_percentage = percentage

    def set_message(self, message: str, duration: int = 180):
        """
        Set status message

        Args:
            message: Message to display
            duration: Duration in frames (180 = 3 seconds at 60 FPS)
        """
        self.message = message
        self.message_timer = duration

    def reset_game(self):
        """Reset the game to initial state"""
        # Reset the game engine
        self.game.reset_game()

        # Reset GUI state
        self.game_over = False
        self.final_game_state = None
        self.showing_raise_input = False
        self.raise_amount = 0
        self.raise_percentage = 0.0
        self.message = ""
        self.message_timer = 0

        # Start a new hand
        self.game.start_new_hand()
        self.set_message("Game restarted! Good luck!")

    def toggle_chat(self):
        """Toggle chat panel visibility"""
        if self.chat_panel:
            self.chat_visible = not self.chat_visible
            status = "shown" if self.chat_visible else "hidden"
            self.set_message(f"Chat panel {status} (Tab to toggle)")

    def _action_to_string(self, action: ActionType, amount: int = 0) -> str:
        """Convert action to readable string"""
        if action == ActionType.FOLD:
            return "Fold"
        elif action == ActionType.CHECK:
            return "Check"
        elif action == ActionType.CALL:
            return f"Call ${amount}"
        elif action == ActionType.RAISE:
            return f"Raise to ${amount}"
        elif action == ActionType.ALL_IN:
            return "All In!"
        else:
            return str(action)
