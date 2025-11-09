#!/usr/bin/env python3
"""
Debug Hand Search - Test what hands are in poker-memory and how search works

This script helps diagnose "wrong hands" issues by:
1. Listing all hands in the poker-memory index
2. Testing semantic search with different queries
3. Showing what the LLM would actually see
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from poker_ev.memory.hand_history import HandHistory
from poker_ev.memory.pinecone_store import PineconeMemoryStore
import json

def main():
    print("=" * 80)
    print("🔍 HAND SEARCH DEBUGGER")
    print("=" * 80)

    # Initialize hand history
    try:
        history = HandHistory()
        print(f"✅ Connected to Pinecone index: {history.store.index_name}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    # Get index stats
    print("\n" + "=" * 80)
    print("📊 INDEX STATISTICS")
    print("=" * 80)
    stats = history.store.get_stats()
    print(f"Total vectors: {stats.get('total_vectors', 0)}")
    print(f"Dimension: {stats.get('dimension', 0)}")
    print(f"Index: {stats.get('index_name', 'unknown')}")

    # Get recent hands
    print("\n" + "=" * 80)
    print("📋 RECENT HANDS (All Types)")
    print("=" * 80)
    recent = history.get_recent_hands(limit=10)

    if not recent:
        print("No hands found in database!")
        return

    print(f"Found {len(recent)} recent hands:\n")

    for i, hand in enumerate(recent, 1):
        hand_id = hand.get('hand_id', 'unknown')
        your_cards = hand.get('your_cards', [])
        board = hand.get('board', [])
        outcome = hand.get('outcome', 'unknown')
        profit = hand.get('profit', 0)
        hand_status = hand.get('hand_status', 'unknown')

        # Parse JSON strings if needed
        if isinstance(your_cards, str):
            try:
                your_cards = json.loads(your_cards)
            except:
                pass
        if isinstance(board, str):
            try:
                board = json.loads(board)
            except:
                pass

        cards_str = ', '.join(your_cards) if your_cards else 'None'
        board_str = ', '.join(board) if board else 'None'

        print(f"{i}. {hand_id}")
        print(f"   Status: {hand_status}")
        print(f"   Cards: {cards_str}")
        print(f"   Board: {board_str}")
        print(f"   Outcome: {outcome} | Profit: ${profit:+d}")
        print()

    # Test semantic search with different queries
    print("=" * 80)
    print("🔍 SEMANTIC SEARCH TESTS")
    print("=" * 80)

    test_queries = [
        "pocket aces",
        "ace king",
        "flush draw",
        "top pair",
        "won with strong hand"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)

        # Search with completed filter
        results = history.search_similar_hands(
            query=query,
            limit=3,
            filters={"hand_status": "completed"}
        )

        if not results:
            print("  No results found")
            continue

        for i, hand in enumerate(results, 1):
            hand_id = hand.get('hand_id', 'unknown')
            your_cards = hand.get('your_cards', [])
            similarity = hand.get('similarity_score', 0)
            hand_status = hand.get('hand_status', 'unknown')

            # Parse JSON if needed
            if isinstance(your_cards, str):
                try:
                    your_cards = json.loads(your_cards)
                except:
                    pass

            cards_str = ', '.join(your_cards) if your_cards else 'None'

            print(f"  {i}. Score: {similarity:.3f} | Status: {hand_status}")
            print(f"     ID: {hand_id}")
            print(f"     Cards: {cards_str}")

    # Show hand descriptions (what gets embedded)
    print("\n" + "=" * 80)
    print("📝 HAND DESCRIPTIONS (What gets embedded for search)")
    print("=" * 80)

    for i, hand in enumerate(recent[:3], 1):
        hand_id = hand.get('hand_id', 'unknown')

        # Get the description
        description = hand.get('description', 'No description')

        print(f"\n{i}. {hand_id}")
        print(f"   Description: {description}")

    print("\n" + "=" * 80)
    print("✅ Debugging complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
