"""
Chat Input for retro chat UI

Text input field with blinking cursor and retro styling.
"""

import pygame
from typing import Optional, Callable


class ChatInput:
    """
    Retro-styled text input field for chat
    """

    # Colors - Terminal UI theme
    BG_COLOR = (0, 0, 0)            # Pure black background
    BORDER_COLOR = (0, 255, 0)      # Neon green border
    BORDER_ACTIVE = (0, 255, 0)     # Neon green when active
    TEXT_COLOR = (0, 255, 0)        # Neon green text
    PLACEHOLDER_COLOR = (0, 150, 0) # Dimmed green placeholder
    CURSOR_COLOR = (0, 255, 0)      # Neon green cursor

    def __init__(
        self,
        rect: pygame.Rect,
        font,
        placeholder: str = "Type your message...",
        on_submit: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize chat input

        Args:
            rect: Rectangle for input field
            font: Pygame font for text
            placeholder: Placeholder text when empty
            on_submit: Callback function when Enter is pressed
        """
        self.rect = rect
        self.font = font
        self.placeholder = placeholder
        self.on_submit = on_submit

        # State
        self.text = ""
        self.is_active = False
        self.cursor_pos = 0  # Character position of cursor
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 30  # Frames per blink

        # Scroll offset for long text
        self.scroll_offset = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked inside input
            if self.rect.collidepoint(event.pos):
                self.is_active = True
                # Calculate cursor position from click
                self._update_cursor_from_mouse(event.pos)
                return True
            else:
                self.is_active = False
                return False

        elif event.type == pygame.KEYDOWN and self.is_active:
            return self._handle_keydown(event)

        return False

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """
        Handle keyboard input

        Args:
            event: Pygame KEYDOWN event

        Returns:
            True if handled
        """
        if event.key == pygame.K_RETURN:
            # Submit message
            if self.text.strip():
                if self.on_submit:
                    self.on_submit(self.text)
                self.clear()
            return True

        elif event.key == pygame.K_BACKSPACE:
            # Delete character before cursor
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
                self._update_scroll()
            return True

        elif event.key == pygame.K_DELETE:
            # Delete character after cursor
            if self.cursor_pos < len(self.text):
                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                self._update_scroll()
            return True

        elif event.key == pygame.K_LEFT:
            # Move cursor left
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                self._update_scroll()
            return True

        elif event.key == pygame.K_RIGHT:
            # Move cursor right
            if self.cursor_pos < len(self.text):
                self.cursor_pos += 1
                self._update_scroll()
            return True

        elif event.key == pygame.K_HOME:
            # Move cursor to start
            self.cursor_pos = 0
            self._update_scroll()
            return True

        elif event.key == pygame.K_END:
            # Move cursor to end
            self.cursor_pos = len(self.text)
            self._update_scroll()
            return True

        elif event.unicode and event.unicode.isprintable():
            # Insert character at cursor
            self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
            self.cursor_pos += 1
            self._update_scroll()
            return True

        return False

    def _update_cursor_from_mouse(self, mouse_pos):
        """Update cursor position from mouse click"""
        # Calculate which character was clicked
        relative_x = mouse_pos[0] - self.rect.left - 10 + self.scroll_offset

        # Find closest character position
        for i in range(len(self.text) + 1):
            text_before = self.text[:i]
            width = self.font.size(text_before)[0]

            if width >= relative_x:
                self.cursor_pos = max(0, i - 1) if i > 0 else 0
                return

        self.cursor_pos = len(self.text)

    def _update_scroll(self):
        """Update scroll offset to keep cursor visible"""
        if not self.text:
            self.scroll_offset = 0
            return

        # Calculate cursor pixel position
        text_before_cursor = self.text[:self.cursor_pos]
        cursor_x = self.font.size(text_before_cursor)[0]

        # Available width for text (minus padding)
        available_width = self.rect.width - 20

        # Scroll if cursor is outside visible area
        if cursor_x - self.scroll_offset < 10:
            # Cursor too far left
            self.scroll_offset = max(0, cursor_x - 10)
        elif cursor_x - self.scroll_offset > available_width - 10:
            # Cursor too far right
            self.scroll_offset = cursor_x - available_width + 10

    def clear(self):
        """Clear input text"""
        self.text = ""
        self.cursor_pos = 0
        self.scroll_offset = 0

    def set_text(self, text: str):
        """Set input text programmatically"""
        self.text = text
        self.cursor_pos = len(text)
        self._update_scroll()

    def update(self):
        """Update animation (call every frame)"""
        # Update cursor blink
        self.cursor_timer += 1
        if self.cursor_timer >= self.cursor_blink_rate:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def render(self, screen: pygame.Surface):
        """
        Render the input field with System 6-style inset effect

        Args:
            screen: Pygame surface to draw on
        """
        # Terminal-style: simple neon green border, no shadows or glows
        pygame.draw.rect(screen, self.BG_COLOR, self.rect)
        pygame.draw.rect(screen, self.BORDER_COLOR, self.rect, 1)

        # Create clipping rect for text
        text_area = self.rect.inflate(-20, -10)

        # Draw text or placeholder
        if self.text:
            # Render actual text
            text_surface = self.font.render(self.text, True, self.TEXT_COLOR)
            # Apply scroll offset
            screen.blit(
                text_surface,
                (self.rect.left + 10, self.rect.centery - text_surface.get_height() // 2),
                area=pygame.Rect(
                    self.scroll_offset,
                    0,
                    text_area.width,
                    text_surface.get_height()
                )
            )

            # Draw cursor if active
            if self.is_active and self.cursor_visible:
                self._draw_cursor(screen)
        elif not self.is_active:
            # Show placeholder
            placeholder_surface = self.font.render(self.placeholder, True, self.PLACEHOLDER_COLOR)
            screen.blit(
                placeholder_surface,
                (self.rect.left + 10, self.rect.centery - placeholder_surface.get_height() // 2)
            )

    def _draw_cursor(self, screen: pygame.Surface):
        """Draw blinking cursor"""
        # Calculate cursor position
        text_before_cursor = self.text[:self.cursor_pos]
        cursor_x = self.font.size(text_before_cursor)[0] - self.scroll_offset

        # Cursor position on screen
        cursor_screen_x = self.rect.left + 10 + cursor_x
        cursor_y_top = self.rect.top + 8
        cursor_y_bottom = self.rect.bottom - 8

        # Draw cursor line
        pygame.draw.line(
            screen,
            self.CURSOR_COLOR,
            (cursor_screen_x, cursor_y_top),
            (cursor_screen_x, cursor_y_bottom),
            2
        )


# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Chat Input Test")
    clock = pygame.time.Clock()

    # Load font
    try:
        font = pygame.font.Font("poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf", 18)
    except:
        font = pygame.font.Font(None, 24)

    # Create input field
    input_rect = pygame.Rect(50, 300, 500, 50)

    def on_submit(text):
        print(f"Submitted: {text}")

    chat_input = ChatInput(input_rect, font, on_submit=on_submit)

    # Display text
    display_font = pygame.font.Font(None, 24)
    submitted_messages = []

    def handle_submit(text):
        submitted_messages.append(text)
        if len(submitted_messages) > 5:
            submitted_messages.pop(0)

    chat_input.on_submit = handle_submit

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                chat_input.handle_event(event)

        # Update
        chat_input.update()

        # Clear screen
        screen.fill((20, 20, 20))

        # Draw title
        title = display_font.render("Chat Input Test - Click to focus, type and press Enter", True, (255, 255, 255))
        screen.blit(title, (50, 20))

        # Draw submitted messages
        y = 60
        for msg in submitted_messages:
            msg_surface = display_font.render(f"You: {msg}", True, (0, 255, 100))
            screen.blit(msg_surface, (50, y))
            y += 30

        # Render input
        chat_input.render(screen)

        # Draw info
        info = display_font.render(
            f"Active: {chat_input.is_active} | Text: '{chat_input.text}' | Cursor: {chat_input.cursor_pos}",
            True, (150, 150, 150)
        )
        screen.blit(info, (50, 365))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
