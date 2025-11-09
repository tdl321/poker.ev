"""
Test card format options (unicode, ascii, text)

Verifies that GameContextProvider supports all three card display formats.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from texasholdem import Card
from poker_ev.llm.game_context import GameContextProvider
from poker_ev.engine.game_wrapper import PokerGame


def test_unicode_format():
    """Test Unicode symbols format (default)"""
    print("\n" + "="*70)
    print("TEST: Unicode Format (Default)")
    print("="*70)

    game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)
    context = GameContextProvider(game, card_format='unicode')

    test_cases = [
        (Card('As'), 'A♠'),
        (Card('Kh'), 'K♥'),
        (Card('Qd'), 'Q♦'),
        (Card('Jc'), 'J♣'),
        (Card('Ts'), 'T♠'),
    ]

    print("\n🎴 Unicode Format Examples:")
    all_passed = True

    for card, expected in test_cases:
        result = context.card_to_string(card)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {card} → '{result}' (expected '{expected}')")
        if result != expected:
            all_passed = False

    # Test pocket pair
    pocket_kings = context.cards_to_string([Card('Kd'), Card('Kc')])
    expected_pair = "K♦ K♣"
    status = "✅" if pocket_kings == expected_pair else "❌"
    print(f"\n   {status} Pocket Kings: '{pocket_kings}' (expected '{expected_pair}')")
    if pocket_kings != expected_pair:
        all_passed = False

    return all_passed


def test_ascii_format():
    """Test ASCII format (single letter suits)"""
    print("\n" + "="*70)
    print("TEST: ASCII Format")
    print("="*70)

    game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)
    context = GameContextProvider(game, card_format='ascii')

    test_cases = [
        (Card('As'), 'As'),
        (Card('Kh'), 'Kh'),
        (Card('Qd'), 'Qd'),
        (Card('Jc'), 'Jc'),
        (Card('Ts'), 'Ts'),
    ]

    print("\n📝 ASCII Format Examples:")
    all_passed = True

    for card, expected in test_cases:
        result = context.card_to_string(card)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {card} → '{result}' (expected '{expected}')")
        if result != expected:
            all_passed = False

    # Test pocket pair
    pocket_kings = context.cards_to_string([Card('Kd'), Card('Kc')])
    expected_pair = "Kd Kc"
    status = "✅" if pocket_kings == expected_pair else "❌"
    print(f"\n   {status} Pocket Kings: '{pocket_kings}' (expected '{expected_pair}')")
    if pocket_kings != expected_pair:
        all_passed = False

    return all_passed


def test_text_format():
    """Test text format (full card names)"""
    print("\n" + "="*70)
    print("TEST: Text Format (Full Names)")
    print("="*70)

    game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)
    context = GameContextProvider(game, card_format='text')

    test_cases = [
        (Card('As'), 'Ace of spades'),
        (Card('Kh'), 'King of hearts'),
        (Card('Qd'), 'Queen of diamonds'),
        (Card('Jc'), 'Jack of clubs'),
        (Card('Ts'), 'Ten of spades'),
        (Card('2h'), 'Two of hearts'),
    ]

    print("\n📖 Text Format Examples:")
    all_passed = True

    for card, expected in test_cases:
        result = context.card_to_string(card)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {card} → '{result}' (expected '{expected}')")
        if result != expected:
            all_passed = False

    # Test pocket pair
    pocket_kings = context.cards_to_string([Card('Kd'), Card('Kc')])
    expected_pair = "King of diamonds, King of clubs"
    status = "✅" if pocket_kings == expected_pair else "❌"
    print(f"\n   {status} Pocket Kings:\n      '{pocket_kings}'\n      (expected '{expected_pair}')")
    if pocket_kings != expected_pair:
        all_passed = False

    return all_passed


def test_all_formats():
    """Test all three formats with the same cards"""
    print("\n" + "="*70)
    print("TEST: Format Comparison")
    print("="*70)

    game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)

    # Create contexts for each format
    context_unicode = GameContextProvider(game, card_format='unicode')
    context_ascii = GameContextProvider(game, card_format='ascii')
    context_text = GameContextProvider(game, card_format='text')

    # Test with Pocket Kings
    kd = Card('Kd')
    kc = Card('Kc')

    unicode_result = context_unicode.cards_to_string([kd, kc])
    ascii_result = context_ascii.cards_to_string([kd, kc])
    text_result = context_text.cards_to_string([kd, kc])

    print("\n🎯 Pocket Kings in all formats:")
    print(f"   Unicode: {unicode_result}")
    print(f"   ASCII:   {ascii_result}")
    print(f"   Text:    {text_result}")

    expected_results = {
        'unicode': "K♦ K♣",
        'ascii': "Kd Kc",
        'text': "King of diamonds, King of clubs"
    }

    all_passed = True
    if unicode_result != expected_results['unicode']:
        print(f"   ❌ Unicode mismatch: expected '{expected_results['unicode']}'")
        all_passed = False
    if ascii_result != expected_results['ascii']:
        print(f"   ❌ ASCII mismatch: expected '{expected_results['ascii']}'")
        all_passed = False
    if text_result != expected_results['text']:
        print(f"   ❌ Text mismatch: expected '{expected_results['text']}'")
        all_passed = False

    if all_passed:
        print("\n   ✅ All formats working correctly!")

    return all_passed


if __name__ == "__main__":
    print("\n🧪 CARD FORMAT TEST SUITE")
    print("="*70)

    results = []
    results.append(("Unicode Format", test_unicode_format()))
    results.append(("ASCII Format", test_ascii_format()))
    results.append(("Text Format", test_text_format()))
    results.append(("Format Comparison", test_all_formats()))

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status}: {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 ALL CARD FORMAT TESTS PASSED!")
        print("\nAvailable formats:")
        print("   • unicode: A♠ K♥ (default, best for visual display)")
        print("   • ascii:   As Kh (terminal-safe, no special characters)")
        print("   • text:    Ace of spades, King of hearts (most readable)")
    else:
        print("\n❌ SOME TESTS FAILED")

    print("="*70)

    assert all_passed, "Card format tests failed!"
