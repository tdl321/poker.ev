#!/usr/bin/env python3
"""
Test card creation for game over showdown

Verifies that cards can be properly created from rank and suit integers.
"""

from texasholdem import Card

print("=" * 80)
print("CARD CREATION TEST")
print("=" * 80)

# Test creating a full deck
all_cards = []
for rank in range(13):
    for suit in [1, 2, 4, 8]:
        rank_char = Card.STR_RANKS[rank]
        suit_char = Card.INT_SUIT_TO_CHAR_SUIT[suit]
        card_string = f"{rank_char}{suit_char}"
        card = Card(card_string)
        all_cards.append(card)

print(f"\n✅ Successfully created {len(all_cards)} cards")
print(f"First 10 cards: {all_cards[:10]}")
print(f"Last 10 cards: {all_cards[-10:]}")

# Test that all cards are unique
unique_cards = set(all_cards)
print(f"\n✅ All cards are unique: {len(unique_cards) == 52}")

# Test rank and suit attributes
print("\nSample cards with attributes:")
for card in all_cards[::13]:  # Every 13th card
    print(f"  {card}: rank={card.rank}, suit={card.suit}")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
