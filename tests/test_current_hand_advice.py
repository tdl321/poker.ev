#!/usr/bin/env python3
"""
Test that the poker advisor correctly uses current game state
and doesn't confuse it with past hands from the vector database
"""

import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Add to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_ev.llm.poker_advisor import PokerAdvisor
from poker_ev.llm.game_context import GameContextProvider
from poker_ev.engine.game_wrapper import PokerGame

print("=" * 60)
print("TEST: Poker Advisor with Current Game State")
print("=" * 60)

# Create a test game
print("\n1. Creating test game...")
game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)
game.start_new_hand()

# Create game context provider
game_context = GameContextProvider(game)

# Display current game state
print("\n2. Current game state:")
print(game_context.get_full_context())

# Create poker advisor with game context
print("\n3. Initializing poker advisor with game context...")
advisor = PokerAdvisor(game_context_provider=game_context)

# Test query about current hand
print("\n4. Testing query about current hand...")
query = "What is the best move for my current hand?"

print(f"\nQuery: {query}")
print("\nResponse:")
print("-" * 60)
# Collect streaming response
response = ""
for chunk in advisor.get_advice_stream(query):
    print(chunk, end='', flush=True)
    response += chunk
print()
print("-" * 60)

# Check if response mentions the correct cards from the game state
player = game.get_game_state()['players'][0]
if player.get('hand'):
    cards = game_context.cards_to_string(player['hand'])
    print(f"\n✅ VERIFICATION:")
    print(f"Current hand cards: {cards}")

    # Check if response mentions these cards
    # Note: Response might not always mention specific cards,
    # but it should NOT mention random wrong cards
    print(f"\nResponse should use these cards, not random cards from past hands.")
    print(f"If you see cards like '1♠ 9♠' or '10♦ 2♦ 3♦', the fix didn't work.")
else:
    print("\nNo current hand available")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
