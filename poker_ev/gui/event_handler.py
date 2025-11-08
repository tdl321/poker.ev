"""
Event handler for converting Pygame events to game actions
"""

import pygame
from texasholdem import ActionType
from typing import Dict, Optional, Callable


class EventHandler:
    """
    Handle Pygame events and convert to game actions

    This class manages user input (mouse clicks, keyboard) and translates
    them into poker actions that the game engine can process.
    """

    def __init__(self, gui):
        """
        Initialize event handler

        Args:
            gui: Reference to the main GUI object
        """
        self.gui = gui
        self.button_rects: Dict[ActionType, pygame.Rect] = {}
        self.raise_slider_rect: Optional[pygame.Rect] = None
        self.raise_confirm_rect: Optional[pygame.Rect] = None

    def register_button(self, action: ActionType, rect: pygame.Rect):
        """
        Register a clickable action button

        Args:
            action: The ActionType this button represents
            rect: The pygame Rect for click detection
        """
        self.button_rects[action] = rect

    def register_raise_slider(self, rect: pygame.Rect):
        """Register the raise amount slider"""
        self.raise_slider_rect = rect

    def register_raise_confirm(self, rect: pygame.Rect):
        """Register the raise confirm button"""
        self.raise_confirm_rect = rect

    def clear_buttons(self):
        """Clear all registered buttons (called each frame before re-registering)"""
        self.button_rects.clear()
        self.raise_slider_rect = None
        self.raise_confirm_rect = None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Process a Pygame event

        Args:
            event: The Pygame event to process

        Returns:
            True if event was handled, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self.handle_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            return self.handle_keypress(event.key)

        return False

    def handle_click(self, pos: tuple) -> bool:
        """
        Handle mouse click

        Args:
            pos: (x, y) position of the click

        Returns:
            True if click was handled, False otherwise
        """
        # Check action buttons
        for action, rect in self.button_rects.items():
            if rect.collidepoint(pos):
                self.gui.handle_action_click(action)
                return True

        # Check raise slider
        if self.raise_slider_rect and self.raise_slider_rect.collidepoint(pos):
            self.handle_slider_click(pos)
            return True

        # Check raise confirm
        if self.raise_confirm_rect and self.raise_confirm_rect.collidepoint(pos):
            self.gui.confirm_raise()
            return True

        return False

    def handle_slider_click(self, pos: tuple):
        """
        Handle click on raise slider

        Args:
            pos: (x, y) position of the click
        """
        if not self.raise_slider_rect:
            return

        # Calculate raise amount based on slider position
        slider_x = self.raise_slider_rect.x
        slider_width = self.raise_slider_rect.width
        click_x = pos[0]

        # Calculate percentage (0.0 to 1.0)
        percentage = max(0.0, min(1.0, (click_x - slider_x) / slider_width))

        # Update GUI's raise amount
        self.gui.update_raise_amount(percentage)

    def handle_keypress(self, key: int) -> bool:
        """
        Handle keyboard input

        Args:
            key: Pygame key constant

        Returns:
            True if key was handled, False otherwise
        """
        # Action shortcuts
        if key == pygame.K_f:
            self.gui.handle_action_click(ActionType.FOLD)
            return True
        elif key == pygame.K_c:
            # Could be CHECK or CALL depending on valid actions
            valid_actions = self.gui.game.get_game_state()['valid_actions']
            if ActionType.CHECK in valid_actions:
                self.gui.handle_action_click(ActionType.CHECK)
            elif ActionType.CALL in valid_actions:
                self.gui.handle_action_click(ActionType.CALL)
            return True
        elif key == pygame.K_r:
            self.gui.handle_action_click(ActionType.RAISE)
            return True
        elif key == pygame.K_a:
            self.gui.handle_action_click(ActionType.ALL_IN)
            return True

        # UI controls
        elif key == pygame.K_ESCAPE:
            # Cancel raise input
            self.gui.cancel_raise()
            return True

        return False
