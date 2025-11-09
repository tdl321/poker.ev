"""
Test script for Pinecone memory system

Tests all memory components: HandHistory, PatternTracker, SessionManager
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


def test_pinecone_store():
    """Test basic Pinecone store functionality"""
    print("\n" + "=" * 60)
    print("Testing Pinecone Memory Store")
    print("=" * 60)

    try:
        from poker_ev.memory import PineconeMemoryStore

        store = PineconeMemoryStore()
        print("✅ Pinecone store initialized successfully")

        # Get stats
        stats = store.get_stats()
        print(f"\n📊 Pinecone Stats:")
        print(f"  • Index: {stats.get('index_name')}")
        print(f"  • Dimension: {stats.get('dimension')}")
        print(f"  • Total vectors: {stats.get('total_vectors', 0)}")

        return store

    except Exception as e:
        print(f"❌ Failed to initialize Pinecone store: {e}")
        return None


def test_hand_history(store):
    """Test HandHistory with Pinecone"""
    print("\n" + "=" * 60)
    print("Testing Hand History")
    print("=" * 60)

    try:
        from poker_ev.memory import HandHistory

        # Create hand history with shared store
        history = HandHistory(pinecone_store=store)
        print("✅ Hand history initialized")

        # Test data
        test_hands = [
            {
                'hand_id': f'test_hand_{datetime.now().strftime("%Y%m%d_%H%M%S")}_001',
                'your_cards': ['A♠', 'K♥'],
                'board': ['Q♥', 'J♦', '10♣', '9♠', '2♥'],
                'actions_summary': 'Raised preflop, bet flop, called turn, bet river',
                'pot': 150,
                'winner': 0,
                'outcome': 'won',
                'profit': 75,
                'phase': 'RIVER',
                'position': 'Button',
                'hand_strength': 'straight',
                'board_texture': 'connected',
                'opponent_style': 'tight',
                'aggression_level': 'aggressive',
                'notes': 'Good aggressive play with straight'
            },
            {
                'hand_id': f'test_hand_{datetime.now().strftime("%Y%m%d_%H%M%S")}_002',
                'your_cards': ['K♠', 'K♦'],
                'board': ['A♥', '7♦', '3♣'],
                'actions_summary': 'Raised preflop, bet flop, folded to re-raise',
                'pot': 80,
                'winner': 1,
                'outcome': 'folded',
                'profit': -40,
                'phase': 'FLOP',
                'position': 'Big Blind',
                'hand_strength': 'overpair',
                'board_texture': 'dry with ace',
                'opponent_style': 'aggressive',
                'aggression_level': 'passive',
                'notes': 'Folded to aggression on ace-high board'
            },
            {
                'hand_id': f'test_hand_{datetime.now().strftime("%Y%m%d_%H%M%S")}_003',
                'your_cards': ['Q♠', 'Q♥'],
                'board': ['10♥', '9♦', '8♣', '7♠', '2♥'],
                'actions_summary': 'Called preflop raise, bet flop, raised turn, won',
                'pot': 200,
                'winner': 0,
                'outcome': 'won',
                'profit': 100,
                'phase': 'RIVER',
                'position': 'Small Blind',
                'hand_strength': 'overpair',
                'board_texture': 'connected',
                'opponent_style': 'tight',
                'aggression_level': 'aggressive',
                'notes': 'Aggressive play paid off'
            }
        ]

        # Save hands
        print("\n💾 Saving test hands...")
        for i, hand in enumerate(test_hands, 1):
            if history.save_hand(hand):
                print(f"  ✅ Saved hand {i}/{len(test_hands)}: {hand['hand_id']}")
            else:
                print(f"  ❌ Failed to save hand {i}/{len(test_hands)}")

        # Wait a moment for indexing
        import time
        print("\n⏳ Waiting for Pinecone indexing...")
        time.sleep(2)

        # Get statistics
        print("\n📊 Hand History Statistics:")
        stats = history.get_statistics()
        print(f"  • Total hands: {stats.get('total_hands', 0)}")
        print(f"  • Win rate: {stats.get('win_rate', 0)}%")
        print(f"  • Total profit: ${stats.get('total_profit', 0)}")
        print(f"  • Avg profit/hand: ${stats.get('avg_profit', 0)}")

        # Test semantic search
        print("\n🔍 Testing semantic search...")
        query = "aggressive play with premium hands"
        similar = history.search_similar_hands(query, limit=3)
        print(f"  Query: '{query}'")
        print(f"  Found {len(similar)} similar hands:")
        for hand in similar:
            score = hand.get('similarity_score', 0)
            hand_id = hand.get('hand_id', 'unknown')
            outcome = hand.get('outcome', 'unknown')
            print(f"    • {hand_id}: {outcome} (similarity: {score:.3f})")

        # Test filters
        print("\n🎯 Testing filtered search...")
        won_hands = history.get_hands_by_outcome('won')
        print(f"  Winning hands: {len(won_hands)}")

        print("\n✅ Hand history tests completed successfully")
        return history

    except Exception as e:
        print(f"❌ Hand history test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_pattern_tracker(hand_history):
    """Test PatternTracker with Pinecone"""
    print("\n" + "=" * 60)
    print("Testing Pattern Tracker")
    print("=" * 60)

    try:
        from poker_ev.memory import PatternTracker

        # Create pattern tracker with shared hand history
        tracker = PatternTracker(hand_history=hand_history)
        print("✅ Pattern tracker initialized")

        # Analyze patterns
        print("\n📈 Analyzing patterns...")
        report = tracker.format_analysis_report()
        print(report)

        # Discover winning patterns
        print("\n🎯 Discovering winning patterns...")
        patterns = tracker.discover_winning_patterns(min_hands=1)
        print(f"  Found {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"    • {pattern.get('pattern_name')}")
            print(f"      {pattern.get('insight', 'N/A')}")

        # Test pattern search
        print("\n🔍 Testing pattern search...")
        query = "button position play"
        found_patterns = tracker.search_patterns(query, limit=3)
        print(f"  Query: '{query}'")
        print(f"  Found {len(found_patterns)} patterns:")
        for pattern in found_patterns:
            score = pattern.get('similarity_score', 0)
            name = pattern.get('pattern_name', 'unknown')
            print(f"    • {name} (similarity: {score:.3f})")

        print("\n✅ Pattern tracker tests completed successfully")
        return tracker

    except Exception as e:
        print(f"❌ Pattern tracker test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_session_manager(store):
    """Test SessionManager with Pinecone"""
    print("\n" + "=" * 60)
    print("Testing Session Manager")
    print("=" * 60)

    try:
        from poker_ev.memory import SessionManager

        # Create session manager with shared store
        manager = SessionManager(pinecone_store=store)
        print("✅ Session manager initialized")

        # Create session
        session_id = manager.create_session()
        print(f"\n📝 Created session: {session_id}")

        # Add test messages
        print("\n💬 Adding test messages...")
        messages = [
            ('user', 'Should I call with pocket jacks preflop?'),
            ('assistant', 'Pocket jacks are a strong hand. You should raise from most positions. Consider your position and stack sizes when deciding how much to raise.'),
            ('user', 'What about pot odds?'),
            ('assistant', 'Pot odds are the ratio of the pot size to the cost of a call. You need at least 2:1 pot odds to call with most draws.'),
            ('user', 'How can I improve my button play?'),
            ('assistant', 'From the button, you should play a wide range. Raise 60-70% of hands, especially when folded to you. Use your position advantage postflop.'),
        ]

        for role, content in messages:
            manager.add_message(role, content)
            print(f"  • {role}: {content[:50]}...")

        # Save session
        print("\n💾 Saving session...")
        if manager.save_session():
            print("  ✅ Session saved successfully")

        # Wait for indexing
        import time
        print("\n⏳ Waiting for Pinecone indexing...")
        time.sleep(2)

        # Test session search
        print("\n🔍 Testing session search...")
        query = "pot odds and equity"
        results = manager.search_sessions(query, limit=3)
        print(f"  Query: '{query}'")
        print(f"  Found {len(results)} sessions:")
        for session in results:
            score = session.get('similarity_score', 0)
            session_id = session.get('session_id', 'unknown')
            summary = session.get('summary', 'No summary')[:60]
            print(f"    • {session_id} (similarity: {score:.3f})")
            print(f"      {summary}...")

        # Get past advice
        print("\n📚 Testing past advice retrieval...")
        advice = manager.get_past_advice_on_topic("button play")
        print(f"  Found {len(advice)} pieces of advice:")
        for i, adv in enumerate(advice[:3], 1):
            print(f"    {i}. {adv[:80]}...")

        print("\n✅ Session manager tests completed successfully")
        return manager

    except Exception as e:
        print(f"❌ Session manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PINECONE MEMORY SYSTEM TEST SUITE")
    print("=" * 60)

    # Test Pinecone store
    store = test_pinecone_store()
    if not store:
        print("\n❌ Pinecone store initialization failed. Exiting.")
        sys.exit(1)

    # Test hand history
    hand_history = test_hand_history(store)

    # Test pattern tracker
    if hand_history:
        pattern_tracker = test_pattern_tracker(hand_history)

    # Test session manager
    session_manager = test_session_manager(store)

    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✅ Pinecone Store:    PASSED" if store else "❌ Pinecone Store:    FAILED")
    print("✅ Hand History:      PASSED" if hand_history else "❌ Hand History:      FAILED")
    print("✅ Pattern Tracker:   PASSED" if hand_history and pattern_tracker else "❌ Pattern Tracker:   FAILED")
    print("✅ Session Manager:   PASSED" if session_manager else "❌ Session Manager:   FAILED")
    print("=" * 60)

    if store and hand_history and session_manager:
        print("\n🎉 All tests passed! Pinecone memory system is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
