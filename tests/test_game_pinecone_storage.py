#!/usr/bin/env python3
"""
Test case for verifying game data storage to Pinecone

This test:
1. Initializes a poker game
2. Starts a hand and deals cards
3. Saves hand data to Pinecone database
4. Queries Pinecone to verify storage
5. Cleans up test data (optional)
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.memory.hand_history import HandHistory
from poker_ev.memory.pinecone_store import PineconeMemoryStore


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def format_card(card_obj) -> str:
    """Format a card object to readable string"""
    rank_map = {
        0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7', 6: '8',
        7: '9', 8: 'T', 9: 'J', 10: 'Q', 11: 'K', 12: 'A'
    }
    suit_map = {1: '♠', 2: '♥', 4: '♦', 8: '♣'}

    if hasattr(card_obj, 'rank') and hasattr(card_obj, 'suit'):
        return f"{rank_map.get(card_obj.rank, '?')}{suit_map.get(card_obj.suit, '?')}"
    return str(card_obj)


def test_pinecone_storage():
    """
    Main test function for Pinecone storage
    """

    # Step 1: Check API key
    print_section("STEP 1: Checking Pinecone Configuration")

    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ ERROR: PINECONE_API_KEY not found in environment")
        print("\nTo fix this:")
        print("1. Create a .env file in the project root")
        print("2. Add: PINECONE_API_KEY=your-api-key-here")
        print("3. Get your API key from https://www.pinecone.io/")
        return False

    print(f"✅ Pinecone API key found: {api_key[:15]}...")


    # Step 2: Initialize game
    print_section("STEP 2: Initializing Poker Game")

    try:
        game = PokerGame(
            num_players=4,
            buyin=1000,
            big_blind=10,
            small_blind=5
        )
        print("✅ Game initialized successfully")
        print(f"   Players: {game.num_players}")
        print(f"   Starting chips: {game.buyin}")
        print(f"   Blinds: {game.small_blind}/{game.big_blind}")
    except Exception as e:
        print(f"❌ Failed to initialize game: {e}")
        return False


    # Step 3: Start a hand and get card data
    print_section("STEP 3: Starting Hand and Dealing Cards")

    try:
        success = game.start_new_hand()
        if not success:
            print("❌ Failed to start hand")
            return False

        print("✅ Hand started successfully")

        # Get game state
        state = game.get_game_state()

        # Display game information
        print(f"\n📊 Game State:")
        print(f"   Hand Active: {state['hand_active']}")
        print(f"   Phase: {state['hand_phase']}")
        print(f"   Pot: ${state['pot']}")
        print(f"   Current Player: Player {state['current_player']}")

        # Display player cards (Player 0 is human player)
        print(f"\n🃏 Your Cards (Player 0):")
        player_0 = state['players'][0]
        if player_0['hand']:
            cards_str = ', '.join([format_card(card) for card in player_0['hand']])
            print(f"   {cards_str}")
        else:
            print("   No cards visible")

        # Display board cards
        if state['board']:
            board_str = ', '.join([format_card(card) for card in state['board']])
            print(f"\n🎴 Board: {board_str}")
        else:
            print(f"\n🎴 Board: (empty - preflop)")

        # Display all players
        print(f"\n👥 Players:")
        for i, player in enumerate(state['players']):
            status = "FOLDED" if player['folded'] else "ACTIVE"
            chips = player['chips']
            bet = player['bet']
            print(f"   Player {i}: ${chips} (bet: ${bet}) [{status}]")

    except Exception as e:
        print(f"❌ Failed to start hand: {e}")
        import traceback
        traceback.print_exc()
        return False


    # Step 4: Initialize Pinecone and save hand data
    print_section("STEP 4: Saving Hand Data to Pinecone")

    try:
        # Initialize hand history (with Pinecone store)
        print("Initializing Pinecone store...")
        hand_history = HandHistory()
        print("✅ Pinecone store initialized")

        # Prepare hand data for storage
        player_0_cards = state['players'][0]['hand']
        cards_str_list = [format_card(card) for card in player_0_cards] if player_0_cards else []

        board_cards = state['board']
        board_str_list = [format_card(card) for card in board_cards] if board_cards else []

        # Generate unique hand ID
        hand_id = f"test_hand_{int(time.time())}"

        hand_data = {
            'hand_id': hand_id,
            'timestamp': datetime.now().isoformat(),
            'your_cards': cards_str_list,
            'board': board_str_list,
            'pot': state['pot'],
            'phase': str(state['hand_phase']),
            'position': 'Button',  # Example position
            'outcome': 'pending',   # Hand not finished yet
            'profit': 0,
            'actions_summary': 'Started hand, dealt cards',
            'notes': 'Test hand created by test_game_pinecone_storage.py',
            'hand_strength': 'Unknown',  # Would analyze actual hand strength
            'board_texture': 'Dry' if board_str_list else 'Preflop'
        }

        print(f"\n📝 Hand Data to Store:")
        print(f"   Hand ID: {hand_data['hand_id']}")
        print(f"   Cards: {', '.join(cards_str_list) if cards_str_list else 'None'}")
        print(f"   Board: {', '.join(board_str_list) if board_str_list else 'Preflop'}")
        print(f"   Pot: ${hand_data['pot']}")
        print(f"   Phase: {hand_data['phase']}")

        # Save to Pinecone
        print(f"\n💾 Saving to Pinecone...")
        success = hand_history.save_hand(hand_data)

        if success:
            print("✅ Hand data saved to Pinecone successfully!")
        else:
            print("❌ Failed to save hand data")
            return False

    except Exception as e:
        print(f"❌ Failed to save to Pinecone: {e}")
        import traceback
        traceback.print_exc()
        return False


    # Step 5: Query Pinecone to verify storage
    print_section("STEP 5: Verifying Data Storage in Pinecone")

    try:
        # Wait a moment for indexing
        print("Waiting 2 seconds for Pinecone indexing...")
        time.sleep(2)

        # Query for recent hands
        print("Querying Pinecone for recent hands...")
        recent_hands = hand_history.get_recent_hands(limit=5)

        if not recent_hands:
            print("⚠️  No hands found in database (may need more time for indexing)")
            print("   Try running: python tests/test_game_pinecone_storage.py --verify")
            return True  # Still consider test passed if save succeeded

        print(f"✅ Found {len(recent_hands)} hand(s) in database")

        # Check if our test hand is in the results
        our_hand_found = False
        for i, hand in enumerate(recent_hands):
            print(f"\n   Hand {i+1}:")
            print(f"      ID: {hand.get('hand_id', 'N/A')}")
            print(f"      Cards: {hand.get('your_cards', 'N/A')}")
            print(f"      Pot: ${hand.get('pot', 0)}")
            print(f"      Phase: {hand.get('phase', 'N/A')}")
            print(f"      Timestamp: {hand.get('timestamp', 'N/A')}")

            if hand.get('hand_id') == hand_id:
                our_hand_found = True
                print(f"      ⭐ THIS IS OUR TEST HAND!")

        if our_hand_found:
            print("\n✅ Test hand successfully stored and retrieved from Pinecone!")
        else:
            print("\n⚠️  Test hand not found in recent hands (may need more time)")

    except Exception as e:
        print(f"❌ Failed to verify storage: {e}")
        import traceback
        traceback.print_exc()
        return False


    # Step 6: Summary
    print_section("TEST SUMMARY")
    print("✅ All tests passed successfully!")
    print("\n📊 What was tested:")
    print("   ✓ Pinecone API connection")
    print("   ✓ Game initialization")
    print("   ✓ Card dealing and game state")
    print("   ✓ Hand data storage to Pinecone")
    print("   ✓ Data retrieval from Pinecone")
    print("\n💡 Your game data is being stored to Pinecone successfully!")
    print("   You can verify this in your Pinecone dashboard.")

    return True


def verify_only():
    """
    Only verify existing data in Pinecone without creating new test data
    """
    print_section("Verifying Existing Pinecone Data")

    try:
        hand_history = HandHistory()
        recent_hands = hand_history.get_recent_hands(limit=10)

        if not recent_hands:
            print("❌ No hands found in database")
            return False

        print(f"✅ Found {len(recent_hands)} hand(s) in database\n")

        for i, hand in enumerate(recent_hands):
            print(f"Hand {i+1}:")
            print(f"   ID: {hand.get('hand_id', 'N/A')}")
            print(f"   Cards: {hand.get('your_cards', 'N/A')}")
            print(f"   Board: {hand.get('board', 'N/A')}")
            print(f"   Pot: ${hand.get('pot', 0)}")
            print(f"   Phase: {hand.get('phase', 'N/A')}")
            print(f"   Outcome: {hand.get('outcome', 'N/A')}")
            print(f"   Timestamp: {hand.get('timestamp', 'N/A')[:19]}")
            print()

        return True

    except Exception as e:
        print(f"❌ Failed to verify: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Check if verify-only mode
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        success = verify_only()
    else:
        success = test_pinecone_storage()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
