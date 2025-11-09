"""
Message Renderer for retro chat UI

Renders chat messages with 8-bit pixel art styling.
Supports markdown formatting (bold, italic, headers, bullets).
"""

import pygame
import re
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

    # Card suit symbols that need Unicode font
    SUIT_SYMBOLS = ['♠', '♥', '♦', '♣']

    # Text styling types
    STYLE_NORMAL = 'normal'
    STYLE_BOLD = 'bold'
    STYLE_ITALIC = 'italic'
    STYLE_BOLD_ITALIC = 'bold_italic'
    STYLE_HEADER = 'header'

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

        # Create Unicode-compatible system font for card suit symbols
        # Use same size as medium font for consistency
        medium_height = font_medium.get_height()
        # System font (None) supports Unicode symbols
        self.font_symbols = pygame.font.Font(None, int(medium_height * 1.2))

        # Try to load bold font (fallback to using color for emphasis)
        try:
            # Try to find a bold version of the font
            # For PixeloidMono, we'll use system font with bold flag
            self.font_bold = pygame.font.Font(None, medium_height)
            self.font_bold.set_bold(True)
        except:
            self.font_bold = None

        # Try to load italic font
        try:
            self.font_italic = pygame.font.Font(None, medium_height)
            self.font_italic.set_italic(True)
        except:
            self.font_italic = None

    def parse_markdown(self, text: str) -> List[Tuple[str, str]]:
        """
        Parse markdown text into styled segments

        Supports:
        - **bold**
        - *italic* or _italic_
        - **bold text** with spaces
        - Line breaks preserved

        Args:
            text: Text with markdown formatting

        Returns:
            List of (text_segment, style) tuples
        """
        segments = []

        # Process line by line to preserve line breaks
        lines = text.split('\n')

        for line_idx, line in enumerate(lines):
            if not line.strip():
                # Empty line - preserve it
                segments.append(('\n', self.STYLE_NORMAL))
                continue

            # Check for headers (lines starting with # or ##)
            header_match = re.match(r'^(#{1,2})\s+(.+)$', line)
            if header_match:
                header_level = len(header_match.group(1))
                header_text = header_match.group(2)
                # Remove markdown from header text
                header_text = re.sub(r'\*\*(.+?)\*\*', r'\1', header_text)
                header_text = re.sub(r'\*(.+?)\*', r'\1', header_text)
                segments.append((header_text, self.STYLE_HEADER))
                if line_idx < len(lines) - 1:
                    segments.append(('\n', self.STYLE_NORMAL))
                continue

            # Check for bullet points (lines starting with - or *)
            bullet_match = re.match(r'^[-\*]\s+(.+)$', line)
            if bullet_match:
                bullet_text = bullet_match.group(1)
                segments.append(('• ', self.STYLE_BOLD))  # Use bullet point
                # Parse the rest of the line for inline markdown
                self._parse_inline_markdown(bullet_text, segments)
                if line_idx < len(lines) - 1:
                    segments.append(('\n', self.STYLE_NORMAL))
                continue

            # Parse regular line for inline markdown
            self._parse_inline_markdown(line, segments)

            # Add line break if not last line
            if line_idx < len(lines) - 1:
                segments.append(('\n', self.STYLE_NORMAL))

        return segments

    def _parse_inline_markdown(self, text: str, segments: List):
        """
        Parse inline markdown (bold, italic) in a line of text

        Args:
            text: Text to parse
            segments: List to append parsed segments to
        """
        # Pattern to match **bold** or *italic*
        # Match **text** first (bold), then *text* (italic)
        pattern = r'(\*\*(.+?)\*\*)|(\*(.+?)\*)'

        last_end = 0
        for match in re.finditer(pattern, text):
            # Add any text before this match
            if match.start() > last_end:
                normal_text = text[last_end:match.start()]
                if normal_text:
                    segments.append((normal_text, self.STYLE_NORMAL))

            # Add the matched formatted text
            if match.group(1):  # **bold**
                bold_text = match.group(2)
                segments.append((bold_text, self.STYLE_BOLD))
            elif match.group(3):  # *italic*
                italic_text = match.group(4)
                segments.append((italic_text, self.STYLE_ITALIC))

            last_end = match.end()

        # Add any remaining text
        if last_end < len(text):
            remaining = text[last_end:]
            if remaining:
                segments.append((remaining, self.STYLE_NORMAL))

    def wrap_text(self, text: str, max_width: int) -> List[str]:
        """
        Wrap text to fit within max width (handles mixed fonts and newlines)

        Args:
            text: Text to wrap
            max_width: Maximum width in pixels

        Returns:
            List of wrapped text lines
        """
        # First, split by explicit newlines to preserve formatting
        paragraphs = text.split('\n')
        lines = []

        for paragraph in paragraphs:
            # Handle empty lines (from multiple newlines like \n\n)
            if not paragraph.strip():
                lines.append('')
                continue

            # Wrap each paragraph
            words = paragraph.split(' ')
            current_line = ""

            for word in words:
                test_line = f"{current_line} {word}".strip()
                # Use mixed-font width calculation
                test_width = self._get_mixed_font_width(test_line)

                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        return lines if lines else [text]

    def _get_font_for_style(self, style: str) -> pygame.font.Font:
        """
        Get the appropriate font for a given style

        Args:
            style: Style type (STYLE_NORMAL, STYLE_BOLD, etc.)

        Returns:
            Pygame font object
        """
        if style == self.STYLE_BOLD:
            return self.font_bold if self.font_bold else self.font_medium
        elif style == self.STYLE_ITALIC:
            return self.font_italic if self.font_italic else self.font_medium
        elif style == self.STYLE_HEADER:
            return self.font_bold if self.font_bold else self.font_medium
        else:
            return self.font_medium

    def _get_color_for_style(self, style: str, base_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Get color for a style (can brighten for bold, etc.)

        Args:
            style: Style type
            base_color: Base text color

        Returns:
            Color tuple
        """
        if style == self.STYLE_BOLD or style == self.STYLE_HEADER:
            # Make bold text brighter
            return tuple(min(255, int(c * 1.2)) for c in base_color)
        elif style == self.STYLE_ITALIC:
            # Slightly dimmer for italic
            return tuple(max(0, int(c * 0.9)) for c in base_color)
        else:
            return base_color

    def _render_styled_segment(
        self,
        screen: pygame.Surface,
        text: str,
        style: str,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        handle_suits: bool = True
    ) -> int:
        """
        Render a single styled text segment

        Args:
            screen: Surface to draw on
            text: Text to render
            style: Style type (STYLE_NORMAL, STYLE_BOLD, etc.)
            x: X position
            y: Y position
            color: Base text color
            handle_suits: Whether to handle card suit symbols specially

        Returns:
            Width of rendered text
        """
        # Get font and color for this style
        font = self._get_font_for_style(style)
        styled_color = self._get_color_for_style(style, color)

        # If handling suits, split into segments
        if handle_suits:
            segments = self._split_text_segments(text)
            current_x = x
            total_width = 0

            for segment, is_symbol in segments:
                # Use symbol font for suit symbols, styled font for text
                segment_font = self.font_symbols if is_symbol else font
                segment_color = color if is_symbol else styled_color

                # Render segment
                surface = segment_font.render(segment, True, segment_color)

                # Align vertically
                segment_y = y
                if is_symbol:
                    text_height = font.get_height()
                    symbol_height = surface.get_height()
                    segment_y = y + (text_height - symbol_height) // 2

                screen.blit(surface, (current_x, segment_y))

                # Move x position
                segment_width = surface.get_width()
                current_x += segment_width
                total_width += segment_width

            return total_width
        else:
            # Simple rendering without suit handling
            surface = font.render(text, True, styled_color)
            screen.blit(surface, (x, y))
            return surface.get_width()

    def _get_styled_segment_width(self, text: str, style: str) -> int:
        """
        Get width of a styled text segment

        Args:
            text: Text to measure
            style: Style type

        Returns:
            Width in pixels
        """
        font = self._get_font_for_style(style)

        # Handle suit symbols
        segments = self._split_text_segments(text)
        total_width = 0

        for segment, is_symbol in segments:
            segment_font = self.font_symbols if is_symbol else font
            width = segment_font.size(segment)[0]
            total_width += width

        return total_width

    def _split_text_segments(self, text: str) -> List[Tuple[str, bool]]:
        """
        Split text into segments of regular text and suit symbols

        Args:
            text: Text to split

        Returns:
            List of (segment, is_symbol) tuples
        """
        segments = []
        current_segment = ""
        is_current_symbol = False

        for char in text:
            char_is_symbol = char in self.SUIT_SYMBOLS

            if not current_segment:
                # Start new segment
                current_segment = char
                is_current_symbol = char_is_symbol
            elif char_is_symbol == is_current_symbol:
                # Continue current segment
                current_segment += char
            else:
                # Different type - save current and start new
                segments.append((current_segment, is_current_symbol))
                current_segment = char
                is_current_symbol = char_is_symbol

        # Add final segment
        if current_segment:
            segments.append((current_segment, is_current_symbol))

        return segments

    def _render_mixed_font_line(
        self,
        screen: pygame.Surface,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int]
    ) -> int:
        """
        Render a line with mixed fonts (retro for text, system for symbols)

        Args:
            screen: Surface to draw on
            text: Text to render
            x: X position
            y: Y position
            color: Text color

        Returns:
            Width of rendered text
        """
        segments = self._split_text_segments(text)
        current_x = x
        total_width = 0

        for segment, is_symbol in segments:
            # Choose font based on segment type
            font = self.font_symbols if is_symbol else self.font_medium

            # Render segment
            surface = font.render(segment, True, color)

            # Align vertically (symbols might be different height)
            segment_y = y
            if is_symbol:
                # Center symbol vertically with text
                text_height = self.font_medium.get_height()
                symbol_height = surface.get_height()
                segment_y = y + (text_height - symbol_height) // 2

            screen.blit(surface, (current_x, segment_y))

            # Move x position for next segment
            segment_width = surface.get_width()
            current_x += segment_width
            total_width += segment_width

        return total_width

    def _get_mixed_font_width(self, text: str) -> int:
        """
        Get the width of text with mixed fonts

        Args:
            text: Text to measure

        Returns:
            Width in pixels
        """
        segments = self._split_text_segments(text)
        total_width = 0

        for segment, is_symbol in segments:
            font = self.font_symbols if is_symbol else self.font_medium
            width = font.size(segment)[0]
            total_width += width

        return total_width

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

        # Terminal-style rendering: simple text with mixed fonts for symbols
        text_y = y + self.padding
        for line in lines:
            # Calculate line width for alignment
            line_width = self._get_mixed_font_width(line)

            if align_right:
                # User messages on right
                text_x = x + self.max_width - line_width - self.padding
            else:
                # AI/System messages on left
                text_x = x + self.padding

            # Render line with mixed fonts (retro + Unicode)
            self._render_mixed_font_line(screen, line, text_x, text_y, text_color)
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
