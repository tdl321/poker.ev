"""
Test card rank mapping fix

Verifies that GameContextProvider correctly converts card ranks
to match texasholdem library's 0-indexed system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from texasholdem import Card
from poker_ev.llm.game_context import GameContextProvider
from poker_ev.engine.game_wrapper import PokerGame


def test_card_rank_mapping():
    """Test that card ranks are correctly mapped"""
    print("\n" + "="*70)
    print("TEST: Card Rank Mapping")
    print("="*70)

    # Create game and context provider
    game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)
    context = GameContextProvider(game)

    # Test all card ranks
    test_cases = [
        (Card('2s'), '2♠'),  # rank=0
        (Card('3h'), '3♥'),  # rank=1
        (Card('4d'), '4♦'),  # rank=2
        (Card('5c'), '5♣'),  # rank=3
        (Card('6s'), '6♠'),  # rank=4
        (Card('7h'), '7♥'),  # rank=5
        (Card('8d'), '8♦'),  # rank=6
        (Card('9c'), '9♣'),  # rank=7
        (Card('Ts'), 'T♠'),  # rank=8 (Ten)
        (Card('Jh'), 'J♥'),  # rank=9 (Jack)
        (Card('Qd'), 'Q♦'),  # rank=10 (Queen)
        (Card('Kc'), 'K♣'),  # rank=11 (King) ← THIS WAS THE BUG!
        (Card('As'), 'A♠'),  # rank=12 (Ace)
    ]

    print("\n🧪 Testing card rank conversions:")
    all_passed = True

    for card, expected in test_cases:
        result = context.card_to_string(card)
        status = "✅" if result == expected else "❌"

        if result != expected:
            all_passed = False
            print(f"   {status} {card} (rank={card.rank}) → Got '{result}', Expected '{expected}'")
        else:
            print(f"   {status} {card} (rank={card.rank}) → '{result}'")

    # Test the specific bug case: Pocket Kings
    print("\n🎯 Testing Pocket Kings (the bug case):")
    kd = Card('Kd')  # K♦
    kc = Card('Kc')  # K♣

    kd_str = context.card_to_string(kd)
    kc_str = context.card_to_string(kc)

    pocket_kings = context.cards_to_string([kd, kc])

    print(f"   K♦: rank={kd.rank} → '{kd_str}'")
    print(f"   K♣: rank={kc.rank} → '{kc_str}'")
    print(f"   Pocket Kings: '{pocket_kings}'")

    if pocket_kings == "K♦ K♣":
        print("   ✅ Pocket Kings correctly displayed!")
    else:
        print(f"   ❌ FAIL: Expected 'K♦ K♣', got '{pocket_kings}'")
        all_passed = False

    # Test the other premium pairs
    print("\n🃏 Testing other premium pairs:")
    premium_pairs = [
        ([Card('As'), Card('Ad')], 'A♠ A♦', 'Pocket Aces'),
        ([Card('Ks'), Card('Kd')], 'K♠ K♦', 'Pocket Kings'),
        ([Card('Qs'), Card('Qd')], 'Q♠ Q♦', 'Pocket Queens'),
        ([Card('Js'), Card('Jd')], 'J♠ J♦', 'Pocket Jacks'),
        ([Card('Ts'), Card('Td')], 'T♠ T♦', 'Pocket Tens'),
    ]

    for cards, expected, name in premium_pairs:
        result = context.cards_to_string(cards)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {name}: '{result}' (expected '{expected}')")
        if result != expected:
            all_passed = False

    print("\n" + "="*70)

    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 Card rank mapping is now correct!")
        print("   Auto-injection will now provide accurate card values to the LLM.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("   Card rank mapping still has issues.")

    print("="*70)

    assert all_passed, "Card rank mapping tests failed!"


if __name__ == "__main__":
    test_card_rank_mapping()
