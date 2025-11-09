"""
Message Renderer for retro chat UI

Renders chat messages with 8-bit pixel art styling.
"""

import pygame
from typing import List, Dict, Tuple
from datetime import datetime


class MessageRenderer:
    """
    Renders chat messages with retro 8-bit styling
    """

    # Colors - Terminal UI theme (no bubbles, minimal style)
    BG_DARK = (0, 0, 0)              # Pure black terminal background
    TEXT_AI = (255, 255, 255)        # Pure white for AI responses
    TEXT_USER = (0, 255, 0)          # Neon green for user input
    TEXT_SYSTEM = (255, 255, 255)    # Pure white for system messages (AI prompts)
    BORDER_COLOR = (0, 255, 0)       # Neon green borders
    TIMESTAMP_COLOR = (0, 150, 0)    # Dimmed green for timestamps

    def __init__(self, font_small, font_medium, max_width: int = 350):
        """
        Initialize message renderer

        Args:
            font_small: Small pygame font (for timestamps)
            font_medium: Medium pygame font (for message content)
            max_width: Maximum width for message bubbles
        """
        self.font_small = font_small
        self.font_medium = font_medium
        self.max_width = max_width
        self.padding = 10
        self.line_spacing = 5

    def wrap_text(self, text: str, max_width: int) -> List[str]:
        """
        Wrap text to fit within max width

        Args:
            text: Text to wrap
            max_width: Maximum width in pixels

        Returns:
            List of wrapped text lines
        """
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_surface = self.font_medium.render(test_line, True, (255, 255, 255))

            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else [text]

    def render_message(
        self,
        screen: pygame.Surface,
        message: Dict,
        x: int,
        y: int,
        show_timestamp: bool = False
    ) -> int:
        """
        Render a single message in terminal style (no bubbles)

        Args:
            screen: Pygame surface to draw on
            message: Message dict with 'role', 'content', 'timestamp'
            x: X position
            y: Y position
            show_timestamp: Whether to show timestamp

        Returns:
            Height of rendered message (for positioning next message)
        """
        role = message.get('role', 'user')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '')

        # Determine text color based on role
        if role == 'user':
            text_color = self.TEXT_USER
            align_right = True
        elif role == 'assistant':
            text_color = self.TEXT_AI
            align_right = False
        else:  # system
            text_color = self.TEXT_SYSTEM
            align_right = False

        # Wrap text
        content_width = self.max_width - 2 * self.padding
        lines = self.wrap_text(content, content_width)

        # Calculate message dimensions
        line_height = self.font_medium.get_height()
        message_height = len(lines) * (line_height + self.line_spacing)

        # Terminal-style rendering: simple text, no backgrounds
        text_y = y + self.padding
        for line in lines:
            text_surface = self.font_medium.render(line, True, text_color)

            if align_right:
                # User messages on right
                text_x = x + self.max_width - text_surface.get_width() - self.padding
            else:
                # AI/System messages on left
                text_x = x + self.padding

            screen.blit(text_surface, (text_x, text_y))
            text_y += line_height + self.line_spacing

        return message_height + self.padding * 2  # Add spacing after message

    def _draw_retro_border(self, screen: pygame.Surface, rect: pygame.Rect, role: str):
        """
        Draw System 6-style borders based on role

        Args:
            screen: Surface to draw on
            rect: Rectangle to border
            role: Message role (user, assistant, system)
        """
        if role == 'user':
            # Double border (like active window)
            pygame.draw.rect(screen, self.ACCENT_PRIMARY, rect, 2)
            inner_rect = rect.inflate(-6, -6)
            pygame.draw.rect(screen, self.ACCENT_DIM, inner_rect, 1)
        elif role == 'assistant':
            # Single border
            pygame.draw.rect(screen, self.ACCENT_PRIMARY, rect, 1)
        else:  # system
            # Dashed border pattern
            self._draw_dashed_border(screen, rect)

    def _draw_dashed_border(self, screen: pygame.Surface, rect: pygame.Rect):
        """
        Draw retro dashed border for system messages

        Args:
            screen: Surface to draw on
            rect: Rectangle to border
        """
        dash_length = 8
        gap_length = 4

        # Draw top edge
        x = rect.left
        while x < rect.right:
            end_x = min(x + dash_length, rect.right)
            pygame.draw.line(screen, self.ACCENT_PRIMARY, (x, rect.top), (end_x, rect.top), 1)
            x += dash_length + gap_length

        # Draw bottom edge
        x = rect.left
        while x < rect.right:
            end_x = min(x + dash_length, rect.right)
            pygame.draw.line(screen, self.ACCENT_PRIMARY, (x, rect.bottom - 1), (end_x, rect.bottom - 1), 1)
            x += dash_length + gap_length

        # Draw left edge
        y = rect.top
        while y < rect.bottom:
            end_y = min(y + dash_length, rect.bottom)
            pygame.draw.line(screen, self.ACCENT_PRIMARY, (rect.left, y), (rect.left, end_y), 1)
            y += dash_length + gap_length

        # Draw right edge
        y = rect.top
        while y < rect.bottom:
            end_y = min(y + dash_length, rect.bottom)
            pygame.draw.line(screen, self.ACCENT_PRIMARY, (rect.right - 1, y), (rect.right - 1, end_y), 1)
            y += dash_length + gap_length

    def _format_timestamp(self, timestamp_str: str) -> str:
        """
        Format timestamp for display

        Args:
            timestamp_str: ISO format timestamp string

        Returns:
            Formatted time string (e.g., "14:32")
        """
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%H:%M")
        except Exception:
            return ""

    def calculate_messages_height(self, messages: List[Dict]) -> int:
        """
        Calculate total height needed for all messages

        Args:
            messages: List of message dicts

        Returns:
            Total height in pixels
        """
        total_height = 0

        for message in messages:
            content = message.get('content', '')
            content_width = self.max_width - 2 * self.padding
            lines = self.wrap_text(content, content_width)

            line_height = self.font_medium.get_height()
            message_height = (
                2 * self.padding +
                len(lines) * line_height +
                (len(lines) - 1) * self.line_spacing +
                self.font_small.get_height() + 5 +
                10  # Spacing after message
            )

            total_height += message_height

        return total_height

    def render_typing_indicator(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        animation_frame: int
    ) -> int:
        """
        Render terminal-style typing indicator with blinking cursor

        Args:
            screen: Surface to draw on
            x: X position
            y: Y position
            animation_frame: Frame number for animation (0-60)

        Returns:
            Height of indicator
        """
        # Terminal-style: just text with blinking cursor
        typing_text = "..."
        text_surface = self.font_medium.render(typing_text, True, self.TEXT_AI)
        screen.blit(text_surface, (x + self.padding, y + self.padding))

        # Blinking cursor (blink every 30 frames)
        if animation_frame % 30 < 15:
            cursor_x = x + self.padding + text_surface.get_width() + 2
            cursor_y = y + self.padding
            cursor_height = self.font_medium.get_height()
            pygame.draw.line(screen, self.BORDER_COLOR,
                           (cursor_x, cursor_y),
                           (cursor_x, cursor_y + cursor_height), 2)

        return self.font_medium.get_height() + self.padding * 2


# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("Message Renderer Test")
    clock = pygame.time.Clock()

    # Load font
    try:
        font_small = pygame.font.Font("poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf", 14)
        font_medium = pygame.font.Font("poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf", 18)
    except:
        font_small = pygame.font.Font(None, 18)
        font_medium = pygame.font.Font(None, 24)

    # Create renderer
    renderer = MessageRenderer(font_small, font_medium, max_width=350)

    # Test messages
    messages = [
        {
            'role': 'system',
            'content': 'Poker Advisor Ready! Ask me anything about your hand.',
            'timestamp': datetime.now().isoformat()
        },
        {
            'role': 'user',
            'content': 'Should I call here with pocket jacks? The pot is $150 and I need to call $30.',
            'timestamp': datetime.now().isoformat()
        },
        {
            'role': 'assistant',
            'content': 'With pocket jacks, calling for $30 into a $150 pot is a good play. You\'re getting 5:1 pot odds and JJ is a strong hand. However, be cautious of overcards on the flop.',
            'timestamp': datetime.now().isoformat()
        }
    ]

    frame = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill((20, 20, 20))

        # Render messages
        y = 20
        for msg in messages:
            height = renderer.render_message(screen, msg, 10, y)
            y += height

        # Render typing indicator
        renderer.render_typing_indicator(screen, 10, y, frame)

        pygame.display.flip()
        clock.tick(60)
        frame = (frame + 1) % 60

    pygame.quit()
