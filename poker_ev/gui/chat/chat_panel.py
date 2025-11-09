"""
Chat Panel for poker.ev

Main chat UI component that combines all chat elements.
"""

import pygame
from typing import List, Dict, Optional, Callable
from datetime import datetime
import threading

from poker_ev.gui.chat.scroll_handler import ScrollHandler
from poker_ev.gui.chat.message_renderer import MessageRenderer
from poker_ev.gui.chat.chat_input import ChatInput


class ChatPanel:
    """
    Main chat panel component - always visible side panel

    Combines scrolling, message rendering, and input handling.
    """

    # Colors - Terminal UI theme (black background, neon green)
    BG_DARK = (0, 0, 0)             # Pure black terminal background
    BG_MEDIUM = (0, 0, 0)           # Pure black
    BG_PANEL = (0, 0, 0)            # Pure black
    ACCENT_PRIMARY = (0, 255, 0)    # Neon green (terminal color)
    ACCENT_DIM = (0, 200, 0)        # Dimmed neon green
    TEXT_PRIMARY = (255, 255, 255)  # Pure white (AI responses)
    TEXT_USER = (0, 255, 0)         # Neon green (user input)

    # Legacy aliases for compatibility
    PANEL_BG = BG_MEDIUM
    HEADER_BG = BG_PANEL
    HEADER_TEXT = ACCENT_PRIMARY
    BORDER_COLOR = ACCENT_PRIMARY

    def __init__(
        self,
        panel_rect: pygame.Rect,
        font_small,
        font_medium,
        font_large,
        on_message_send: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize chat panel

        Args:
            panel_rect: Rectangle for entire chat panel
            font_small: Small font (timestamps)
            font_medium: Medium font (messages)
            font_large: Large font (header)
            on_message_send: Callback when user sends message
        """
        self.rect = panel_rect
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large
        self.on_message_send = on_message_send

        # Header
        self.header_height = 60
        self.header_rect = pygame.Rect(
            panel_rect.left,
            panel_rect.top,
            panel_rect.width,
            self.header_height
        )

        # Input area
        self.input_height = 60
        self.input_rect = pygame.Rect(
            panel_rect.left + 10,
            panel_rect.bottom - self.input_height - 10,
            panel_rect.width - 20,
            50
        )

        # Messages area (between header and input)
        self.messages_area = pygame.Rect(
            panel_rect.left,
            panel_rect.top + self.header_height,
            panel_rect.width - 15,  # Leave space for scrollbar
            panel_rect.height - self.header_height - self.input_height - 20
        )

        # Components
        self.scroll_handler = ScrollHandler(self.messages_area, scrollbar_width=12)
        self.message_renderer = MessageRenderer(
            font_small,
            font_medium,
            max_width=panel_rect.width - 40
        )
        self.chat_input = ChatInput(
            self.input_rect,
            font_medium,
            placeholder="Ask about your hand...",
            on_submit=self._handle_message_submit
        )

        # Messages
        self.messages: List[Dict] = []

        # State
        self.is_waiting_response = False
        self.typing_animation_frame = 0

        # Welcome message
        self._add_system_message(
            "Poker Advisor Ready!\n\n"
            "I can help you with:\n"
            "- Hand analysis\n"
            "- Pot odds calculation\n"
            "- Position strategy\n"
            "- Opponent profiling\n\n"
            "Ask me anything!"
        )

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """
        Add a message to the chat

        Args:
            role: 'user', 'assistant', or 'system'
            content: Message content
            metadata: Optional metadata
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.messages.append(message)

        # Update scroll content height
        total_height = self.message_renderer.calculate_messages_height(self.messages)
        self.scroll_handler.set_content_height(total_height)

    def _add_system_message(self, content: str):
        """Add a system message"""
        self.add_message('system', content)

    def _handle_message_submit(self, text: str):
        """Handle user message submission"""
        # Add user message
        self.add_message('user', text)

        # Show typing indicator
        self.is_waiting_response = True

        # Call callback
        if self.on_message_send:
            # Run in thread to avoid blocking
            thread = threading.Thread(
                target=self._process_message_async,
                args=(text,),
                daemon=True
            )
            thread.start()

    def _process_message_async(self, text: str):
        """Process message in background thread"""
        if self.on_message_send:
            self.on_message_send(text)

    def add_ai_response(self, response: str):
        """
        Add AI response to chat

        Args:
            response: AI response text
        """
        self.add_message('assistant', response)
        self.is_waiting_response = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events

        Args:
            event: Pygame event

        Returns:
            True if event was handled (and should not be passed to game)
        """
        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if self.messages_area.collidepoint(mouse_pos):
                self.scroll_handler.handle_mouse_wheel(event)
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Only handle if click is within chat panel area
            if self.rect.collidepoint(mouse_pos):
                self.scroll_handler.handle_mouse_button_down(event)
                # Also check chat input
                return self.chat_input.handle_event(event) or True
            return False

        elif event.type == pygame.MOUSEBUTTONUP:
            self.scroll_handler.handle_mouse_button_up(event)
            # Let scrollbar always handle button up (for drag release)
            # But don't consume the event unless we're dragging
            if self.scroll_handler.is_dragging:
                return True

        elif event.type == pygame.MOUSEMOTION:
            self.scroll_handler.handle_mouse_motion(event)
            # Only consume motion if we're dragging scrollbar
            if self.scroll_handler.is_dragging:
                return True

        # Handle input for keyboard events
        if event.type == pygame.KEYDOWN:
            return self.chat_input.handle_event(event)

        return False

    def update(self):
        """Update animations (call every frame)"""
        self.chat_input.update()

        # Update typing animation
        if self.is_waiting_response:
            self.typing_animation_frame = (self.typing_animation_frame + 1) % 60

    def render(self, screen: pygame.Surface):
        """
        Render the chat panel

        Args:
            screen: Pygame surface to draw on
        """
        mouse_pos = pygame.mouse.get_pos()

        # Draw panel background
        pygame.draw.rect(screen, self.PANEL_BG, self.rect)

        # Draw panel border
        pygame.draw.rect(screen, self.BORDER_COLOR, self.rect, 2)

        # Draw header
        self._render_header(screen)

        # Draw messages
        self._render_messages(screen)

        # Draw scrollbar
        self.scroll_handler.render(screen, mouse_pos)

        # Draw input
        self.chat_input.render(screen)

        # Draw separator line above input
        separator_y = self.input_rect.top - 10
        pygame.draw.line(
            screen,
            self.BORDER_COLOR,
            (self.rect.left, separator_y),
            (self.rect.right, separator_y),
            1
        )

    def _render_header(self, screen: pygame.Surface):
        """Render System 6-style title bar header"""
        # Header background
        pygame.draw.rect(screen, self.HEADER_BG, self.header_rect)

        # Title (centered, single line)
        title = "POKER ADVISOR"
        title_surface = self.font_large.render(title, True, self.HEADER_TEXT)
        title_x = self.header_rect.centerx - title_surface.get_width() // 2
        title_y = self.header_rect.centery - title_surface.get_height() // 2
        screen.blit(title_surface, (title_x, title_y))

        # Bottom border with double line (classic separator)
        pygame.draw.line(
            screen,
            self.ACCENT_PRIMARY,
            (self.header_rect.left, self.header_rect.bottom - 2),
            (self.header_rect.right, self.header_rect.bottom - 2),
            1
        )
        pygame.draw.line(
            screen,
            self.ACCENT_DIM,
            (self.header_rect.left, self.header_rect.bottom - 1),
            (self.header_rect.right, self.header_rect.bottom - 1),
            1
        )

    def _render_messages(self, screen: pygame.Surface):
        """Render all messages with scrolling"""
        # Create clipping rect for messages area
        clip_rect = screen.get_clip()
        screen.set_clip(self.messages_area)

        # Calculate starting Y position
        scroll_offset = self.scroll_handler.get_scroll_offset()
        y = self.messages_area.top - scroll_offset

        # Render each message
        for message in self.messages:
            # Only render if visible
            if y > self.messages_area.bottom:
                break

            height = self.message_renderer.render_message(
                screen,
                message,
                self.messages_area.left,
                y,
                show_timestamp=True
            )

            y += height

        # Render typing indicator if waiting
        if self.is_waiting_response:
            if y >= self.messages_area.top and y <= self.messages_area.bottom:
                self.message_renderer.render_typing_indicator(
                    screen,
                    self.messages_area.left,
                    y,
                    self.typing_animation_frame
                )

        # Restore clipping
        screen.set_clip(clip_rect)

    def clear_messages(self):
        """Clear all messages"""
        self.messages.clear()
        self.scroll_handler.set_content_height(0)
        self._add_system_message("Chat cleared. How can I help?")

    def set_typing(self, is_typing: bool):
        """Set typing indicator state"""
        self.is_waiting_response = is_typing

    def get_messages(self) -> List[Dict]:
        """Get all messages"""
        return self.messages.copy()


# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((500, 800))
    pygame.display.set_caption("Chat Panel Test")
    clock = pygame.time.Clock()

    # Load fonts
    try:
        font_small = pygame.font.Font("poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf", 14)
        font_medium = pygame.font.Font("poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf", 18)
        font_large = pygame.font.Font("poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf", 28)
    except:
        font_small = pygame.font.Font(None, 18)
        font_medium = pygame.font.Font(None, 24)
        font_large = pygame.font.Font(None, 36)

    # Create chat panel
    panel_rect = pygame.Rect(10, 10, 480, 780)

    def handle_message(text: str):
        """Simulate AI response"""
        import time
        time.sleep(1)  # Simulate processing
        chat_panel.add_ai_response(
            f"You asked: '{text}'. This is a test response from the AI advisor."
        )

    chat_panel = ChatPanel(
        panel_rect,
        font_small,
        font_medium,
        font_large,
        on_message_send=handle_message
    )

    # Add some test messages
    chat_panel.add_message(
        'user',
        'Should I call with pocket jacks?'
    )
    chat_panel.add_message(
        'assistant',
        'Pocket jacks are a strong hand, but position matters. What position are you in and what\'s the action in front of you?'
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            else:
                chat_panel.handle_event(event)

        # Update
        chat_panel.update()

        # Clear screen
        screen.fill((15, 15, 15))

        # Render chat panel
        chat_panel.render(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
