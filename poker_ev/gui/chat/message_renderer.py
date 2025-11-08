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

    # Colors - retro theme
    USER_BG = (20, 60, 20)  # Dark green
    USER_BORDER = (0, 255, 100)  # Bright green
    USER_TEXT = (220, 255, 220)  # Light green

    AI_BG = (20, 40, 60)  # Dark blue
    AI_BORDER = (0, 200, 255)  # Cyan
    AI_TEXT = (200, 240, 255)  # Light cyan

    SYSTEM_BG = (60, 50, 20)  # Dark gold
    SYSTEM_BORDER = (255, 215, 0)  # Gold
    SYSTEM_TEXT = (255, 240, 200)  # Light gold

    TIMESTAMP_COLOR = (150, 150, 150)  # Gray

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
        show_timestamp: bool = True
    ) -> int:
        """
        Render a single message bubble

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

        # Get colors based on role
        if role == 'user':
            bg_color = self.USER_BG
            border_color = self.USER_BORDER
            text_color = self.USER_TEXT
            align_right = True
        elif role == 'assistant':
            bg_color = self.AI_BG
            border_color = self.AI_BORDER
            text_color = self.AI_TEXT
            align_right = False
        else:  # system
            bg_color = self.SYSTEM_BG
            border_color = self.SYSTEM_BORDER
            text_color = self.SYSTEM_TEXT
            align_right = False

        # Wrap text
        content_width = self.max_width - 2 * self.padding
        lines = self.wrap_text(content, content_width)

        # Calculate bubble size
        line_height = self.font_medium.get_height()
        bubble_width = self.max_width
        bubble_height = (
            2 * self.padding +
            len(lines) * line_height +
            (len(lines) - 1) * self.line_spacing
        )

        if show_timestamp:
            bubble_height += self.font_small.get_height() + 5

        # Calculate bubble position
        if align_right:
            bubble_x = x + (350 - bubble_width) + 10  # Align to right
        else:
            bubble_x = x + 10  # Align to left

        bubble_rect = pygame.Rect(bubble_x, y, bubble_width, bubble_height)

        # Draw bubble background
        pygame.draw.rect(screen, bg_color, bubble_rect)

        # Draw pixel-art border (retro style)
        self._draw_pixel_border(screen, bubble_rect, border_color)

        # Draw content
        text_y = y + self.padding
        for line in lines:
            text_surface = self.font_medium.render(line, True, text_color)
            screen.blit(text_surface, (bubble_x + self.padding, text_y))
            text_y += line_height + self.line_spacing

        # Draw timestamp
        if show_timestamp and timestamp:
            time_str = self._format_timestamp(timestamp)
            time_surface = self.font_small.render(time_str, True, self.TIMESTAMP_COLOR)

            if align_right:
                time_x = bubble_rect.right - time_surface.get_width() - self.padding
            else:
                time_x = bubble_x + self.padding

            screen.blit(time_surface, (time_x, bubble_rect.bottom - time_surface.get_height() - 3))

        return bubble_height + 10  # Add spacing after message

    def _draw_pixel_border(self, screen: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int]):
        """
        Draw retro pixel-art style border

        Args:
            screen: Surface to draw on
            rect: Rectangle to border
            color: Border color
        """
        # Outer border
        pygame.draw.rect(screen, color, rect, 2)

        # Corner pixels (retro style)
        corner_size = 3
        corners = [
            (rect.left, rect.top),  # Top-left
            (rect.right - corner_size, rect.top),  # Top-right
            (rect.left, rect.bottom - corner_size),  # Bottom-left
            (rect.right - corner_size, rect.bottom - corner_size)  # Bottom-right
        ]

        for corner_x, corner_y in corners:
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(corner_x, corner_y, corner_size, corner_size)
            )

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
        Render animated typing indicator

        Args:
            screen: Surface to draw on
            x: X position
            y: Y position
            animation_frame: Frame number for animation (0-60)

        Returns:
            Height of indicator
        """
        bubble_width = 80
        bubble_height = 40
        bubble_x = x + 10
        bubble_rect = pygame.Rect(bubble_x, y, bubble_width, bubble_height)

        # Draw bubble
        pygame.draw.rect(screen, self.AI_BG, bubble_rect)
        self._draw_pixel_border(screen, bubble_rect, self.AI_BORDER)

        # Animated dots
        dot_radius = 3
        dot_spacing = 12
        center_y = bubble_rect.centery
        start_x = bubble_rect.centerx - dot_spacing

        for i in range(3):
            # Animate dots with bouncing effect
            bounce_offset = 0
            animation_offset = (animation_frame + i * 20) % 60
            if animation_offset < 30:
                bounce_offset = int(-5 * (animation_offset / 30))

            dot_x = start_x + i * dot_spacing
            dot_y = center_y + bounce_offset

            pygame.draw.circle(screen, self.AI_TEXT, (dot_x, dot_y), dot_radius)

        return bubble_height + 10


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
