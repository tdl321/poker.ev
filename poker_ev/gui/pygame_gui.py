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
                 window_size: tuple = (1400, 900)):
        """
        Initialize the Pygame GUI

        Args:
            game: PokerGame instance
            agent_manager: AgentManager for AI players
            window_size: (width, height) of the window
        """
        pygame.init()

        self.game = game
        self.agent_manager = agent_manager
        self.window_size = window_size

        # Create window
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Poker.ev - AI Poker Application")

        # Load assets
        self.load_assets()

        # Initialize components
        self.card_renderer = CardRenderer(self.card_sprites)
        self.event_handler = EventHandler(self)

        # GUI state
        self.showing_raise_input = False
        self.raise_amount = 0
        self.raise_percentage = 0.0

        # Animation state
        self.message = ""
        self.message_timer = 0

        # Player position on table (positions around ellipse)
        self.player_positions = self._calculate_player_positions()

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

        while running and self.game.is_game_running():
            # Start new hand if needed
            if not self.game.is_hand_running():
                self.game.start_new_hand()
                self.set_message("New hand dealt!")

            # Get current game state
            state = self.game.get_game_state()

            # Handle events
            self.event_handler.clear_buttons()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
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

            # Render
            self.render(state)

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
        max_raise = player.chips
        self.raise_amount = int(min_raise + (max_raise - min_raise) * self.raise_percentage)

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

    def render_message(self):
        """Render status message"""
        text = self.font_large.render(self.message, True, self.GOLD_COLOR)
        text_rect = text.get_rect(center=(self.window_size[0] // 2, self.window_size[1] - 50))

        # Background for better visibility
        bg_rect = text_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(self.screen, self.GOLD_COLOR, bg_rect, 2)

        self.screen.blit(text, text_rect)

    # ==================== Action Handlers ====================

    def handle_action_click(self, action: ActionType):
        """Handle action button click from user"""
        if action == ActionType.RAISE:
            # Show raise input
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
        self.showing_raise_input = False
        success = self.game.take_action(ActionType.RAISE, self.raise_amount)

        if success:
            self.set_message(f"You: Raise to ${self.raise_amount}")

    def cancel_raise(self):
        """Cancel raise input"""
        self.showing_raise_input = False

    def update_raise_amount(self, percentage: float):
        """Update raise amount from slider"""
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
