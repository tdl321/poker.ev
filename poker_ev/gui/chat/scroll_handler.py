"""
Scroll Handler for retro chat UI

Manages scrolling for message history with retro styling.
"""

import pygame
from typing import Tuple, Optional


class ScrollHandler:
    """
    Handles scrolling for chat messages with retro-styled scrollbar
    """

    # Colors - monochrome retro theme (system.css inspired)
    BG_DARK = (15, 15, 15)          # Almost black
    BG_PANEL = (35, 35, 35)         # Medium dark
    ACCENT_PRIMARY = (0, 255, 100)  # Retro green
    ACCENT_DIM = (0, 180, 70)       # Dimmed green

    # Legacy aliases
    SCROLLBAR_BG = BG_DARK
    SCROLLBAR_FG = ACCENT_DIM
    SCROLLBAR_HOVER = ACCENT_PRIMARY
    BORDER_COLOR = ACCENT_DIM

    def __init__(self, scroll_area_rect: pygame.Rect, scrollbar_width: int = 12):
        """
        Initialize scroll handler

        Args:
            scroll_area_rect: Rectangle defining the scrollable area
            scrollbar_width: Width of the scrollbar in pixels
        """
        self.scroll_area = scroll_area_rect
        self.scrollbar_width = scrollbar_width

        # Scrollbar position (right edge of scroll area)
        self.scrollbar_rect = pygame.Rect(
            scroll_area_rect.right - scrollbar_width,
            scroll_area_rect.top,
            scrollbar_width,
            scroll_area_rect.height
        )

        # Scroll state
        self.scroll_offset = 0  # Pixels scrolled
        self.content_height = 0  # Total content height
        self.max_scroll = 0  # Maximum scroll offset

        # Dragging state
        self.is_dragging = False
        self.drag_start_y = 0
        self.drag_start_offset = 0

        # Auto-scroll to bottom
        self.auto_scroll = True

    def set_content_height(self, height: int):
        """
        Set the total height of scrollable content

        Args:
            height: Total content height in pixels
        """
        self.content_height = height
        self.max_scroll = max(0, height - self.scroll_area.height)

        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Scroll to the bottom of content"""
        self.scroll_offset = self.max_scroll

    def scroll_to_top(self):
        """Scroll to the top of content"""
        self.scroll_offset = 0

    def scroll_by(self, delta: int):
        """
        Scroll by a relative amount

        Args:
            delta: Pixels to scroll (positive = down, negative = up)
        """
        self.scroll_offset += delta
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

        # Disable auto-scroll if user scrolls up
        if delta < 0 or self.scroll_offset < self.max_scroll:
            self.auto_scroll = False
        elif self.scroll_offset >= self.max_scroll:
            self.auto_scroll = True

    def handle_mouse_wheel(self, event: pygame.event.Event):
        """
        Handle mouse wheel scrolling

        Args:
            event: Pygame MOUSEWHEEL event
        """
        if event.type == pygame.MOUSEWHEEL:
            # Scroll speed: 30 pixels per wheel notch
            scroll_amount = -event.y * 30
            self.scroll_by(scroll_amount)

    def handle_mouse_button_down(self, event: pygame.event.Event):
        """
        Handle mouse button down on scrollbar

        Args:
            event: Pygame MOUSEBUTTONDOWN event
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Check if clicked on scrollbar handle
            handle_rect = self._get_handle_rect()
            if handle_rect and handle_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                self.drag_start_y = mouse_pos[1]
                self.drag_start_offset = self.scroll_offset

    def handle_mouse_button_up(self, event: pygame.event.Event):
        """
        Handle mouse button up

        Args:
            event: Pygame MOUSEBUTTONUP event
        """
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

    def handle_mouse_motion(self, event: pygame.event.Event):
        """
        Handle mouse motion for dragging

        Args:
            event: Pygame MOUSEMOTION event
        """
        if event.type == pygame.MOUSEMOTION and self.is_dragging:
            mouse_y = event.pos[1]
            delta_y = mouse_y - self.drag_start_y

            # Convert mouse delta to scroll delta
            if self.content_height > self.scroll_area.height:
                scroll_ratio = self.content_height / self.scroll_area.height
                scroll_delta = delta_y * scroll_ratio

                self.scroll_offset = self.drag_start_offset + scroll_delta
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

                # Check if at bottom
                if self.scroll_offset >= self.max_scroll:
                    self.auto_scroll = True
                else:
                    self.auto_scroll = False

    def _get_handle_rect(self) -> Optional[pygame.Rect]:
        """
        Get the scrollbar handle rectangle

        Returns:
            Rectangle for the scrollbar handle, or None if not needed
        """
        if self.content_height <= self.scroll_area.height:
            return None  # No scrollbar needed

        # Calculate handle size and position
        visible_ratio = self.scroll_area.height / self.content_height
        handle_height = max(20, int(self.scrollbar_rect.height * visible_ratio))

        # Calculate handle position
        scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
        handle_y_range = self.scrollbar_rect.height - handle_height
        handle_y = self.scrollbar_rect.top + int(handle_y_range * scroll_ratio)

        return pygame.Rect(
            self.scrollbar_rect.left,
            handle_y,
            self.scrollbar_width,
            handle_height
        )

    def is_at_bottom(self) -> bool:
        """Check if scrolled to bottom"""
        return self.scroll_offset >= self.max_scroll - 5  # 5px tolerance

    def render(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """
        Render System 6-style scrollbar

        Args:
            screen: Pygame surface to draw on
            mouse_pos: Current mouse position
        """
        # Only render if content is scrollable
        if self.content_height <= self.scroll_area.height:
            return

        # Scrollbar track (simple outline)
        pygame.draw.rect(screen, self.SCROLLBAR_BG, self.scrollbar_rect)
        pygame.draw.rect(screen, self.BORDER_COLOR, self.scrollbar_rect, 1)

        # Draw scrollbar handle
        handle_rect = self._get_handle_rect()
        if handle_rect:
            # Check if mouse is over handle
            is_hover = handle_rect.collidepoint(mouse_pos) or self.is_dragging
            handle_color = self.SCROLLBAR_HOVER if is_hover else self.SCROLLBAR_FG

            # Fill handle background
            pygame.draw.rect(screen, self.BG_PANEL, handle_rect)

            # Draw handle border
            pygame.draw.rect(screen, handle_color, handle_rect, 2)

            # Draw horizontal grip lines (System 6 style)
            num_lines = 4
            spacing = 3
            center_y = handle_rect.centery
            start_y = center_y - (num_lines // 2) * spacing

            for i in range(num_lines):
                y = start_y + i * spacing
                pygame.draw.line(
                    screen,
                    handle_color,
                    (handle_rect.left + 3, y),
                    (handle_rect.right - 3, y),
                    1
                )

    def get_scroll_offset(self) -> int:
        """Get current scroll offset"""
        return int(self.scroll_offset)

    def is_mouse_over_scrollbar(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if mouse is over scrollbar"""
        return self.scrollbar_rect.collidepoint(mouse_pos)


# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("Scroll Handler Test")
    clock = pygame.time.Clock()

    # Create scroll handler
    scroll_area = pygame.Rect(50, 50, 300, 500)
    scroll_handler = ScrollHandler(scroll_area)

    # Simulate content
    scroll_handler.set_content_height(1500)  # Content taller than view

    # Font for test
    font = pygame.font.Font(None, 24)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                scroll_handler.handle_mouse_wheel(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                scroll_handler.handle_mouse_button_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                scroll_handler.handle_mouse_button_up(event)
            elif event.type == pygame.MOUSEMOTION:
                scroll_handler.handle_mouse_motion(event)

        # Clear screen
        screen.fill((20, 20, 20))

        # Draw scroll area background
        pygame.draw.rect(screen, (40, 40, 40), scroll_area)
        pygame.draw.rect(screen, (0, 255, 100), scroll_area, 2)

        # Draw some test content
        offset = scroll_handler.get_scroll_offset()
        for i in range(50):
            y = scroll_area.top + i * 30 - offset
            if scroll_area.top <= y <= scroll_area.bottom:
                text = font.render(f"Message {i + 1}", True, (255, 255, 255))
                screen.blit(text, (scroll_area.left + 10, y))

        # Render scrollbar
        scroll_handler.render(screen, mouse_pos)

        # Info text
        info = font.render(
            f"Scroll: {scroll_handler.get_scroll_offset()} / {scroll_handler.max_scroll}",
            True, (255, 255, 255)
        )
        screen.blit(info, (50, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
