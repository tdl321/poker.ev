"""
Card renderer for converting texasholdem cards to pygame sprites
"""

import pygame
from texasholdem import Card
from typing import Dict, Optional


class CardRenderer:
    """
    Convert texasholdem Card objects to pyker sprites

    This class handles the mapping between texasholdem's integer-based card
    representation and pyker's image-based sprites.
    """

    # Rank mapping: texasholdem (0-12) → pyker card names
    RANK_MAP = {
        0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7',
        6: '8', 7: '9', 8: '10', 9: 'J', 10: 'Q', 11: 'K', 12: 'A'
    }

    # Suit mapping: texasholdem suit integers → pyker single letters
    # In texasholdem, suits are integers: 1=spades, 2=hearts, 4=diamonds, 8=clubs
    SUIT_MAP = {
        1: 'S',  # spades
        2: 'H',  # hearts
        4: 'D',  # diamonds
        8: 'C',  # clubs
    }

    def __init__(self, card_sprites: Dict[str, pygame.Surface]):
        """
        Initialize card renderer

        Args:
            card_sprites: Dictionary mapping card names to pygame surfaces
                         e.g., {"AS": <Surface>, "KD": <Surface>, ...}
        """
        self.card_sprites = card_sprites

    def card_to_sprite_name(self, card: Card) -> str:
        """
        Convert texasholdem Card to pyker sprite name

        Args:
            card: texasholdem Card object (e.g., Card("Kd"))

        Returns:
            Sprite name (e.g., "KD")

        Examples:
            Card("Kd") → "KD"
            Card("2s") → "2S"
            Card("10h") → "10H"
        """
        rank_str = self.RANK_MAP[card.rank]

        # Get suit - card.suit is an integer bit flag
        suit_int = card.suit
        suit_str = self.SUIT_MAP.get(suit_int)

        if suit_str is None:
            raise ValueError(f"Unknown suit value: {suit_int}")

        return f"{rank_str}{suit_str}"

    def get_card_sprite(self, card: Card, scale: Optional[tuple] = None) -> Optional[pygame.Surface]:
        """
        Get sprite for a card

        Args:
            card: texasholdem Card object
            scale: Optional (width, height) to scale the sprite

        Returns:
            pygame Surface for the card, or None if not found
        """
        sprite_name = self.card_to_sprite_name(card)
        sprite = self.card_sprites.get(sprite_name)

        if sprite is None:
            print(f"Warning: Card sprite '{sprite_name}' not found")
            return None

        if scale is not None:
            sprite = pygame.transform.scale(sprite, scale)

        return sprite

    def get_card_back(self, scale: Optional[tuple] = None) -> Optional[pygame.Surface]:
        """
        Get card back sprite (for hidden cards)

        Args:
            scale: Optional (width, height) to scale the sprite

        Returns:
            pygame Surface for card back
        """
        sprite = self.card_sprites.get("back_red")

        if sprite is None:
            print("Warning: Card back sprite not found")
            return None

        if scale is not None:
            sprite = pygame.transform.scale(sprite, scale)

        return sprite

    def get_cards_sprites(self, cards: list, scale: Optional[tuple] = None) -> list:
        """
        Get sprites for multiple cards

        Args:
            cards: List of texasholdem Card objects
            scale: Optional (width, height) to scale sprites

        Returns:
            List of pygame Surfaces
        """
        return [self.get_card_sprite(card, scale) for card in cards]
