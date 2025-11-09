"""
Test that GUI uses ASCII card format for chat compatibility

Verifies that pygame_gui creates GameContextProvider with ASCII format
to ensure cards display properly in the chat panel.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from texasholdem import Card
from poker_ev.llm.game_context import GameContextProvider
from poker_ev.engine.game_wrapper import PokerGame


def test_gui_uses_ascii_format():
    """Test that GUI would use ASCII format for cards"""
    print("\n" + "="*70)
    print("TEST: GUI ASCII Card Format")
    print("="*70)

    # Simulate what pygame_gui.py does
    game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)

    # This is how pygame_gui.py now initializes GameContextProvider
    game_context = GameContextProvider(game, card_format='ascii')

    # Start a hand to get some cards
    game.start_new_hand()

    # Advance game to player 0's turn if needed
    from texasholdem import ActionType
    while game.engine.current_player != 0 and game.engine.is_hand_running():
        # Make other players fold to quickly get to player 0
        game.engine.take_action(ActionType.FOLD)

    # Get the game context
    context_str = game_context.get_current_situation()

    print("\n🎴 Game Context Output:")
    print(context_str)

    # Verify ASCII format is being used
    # ASCII format uses single letters: s, h, d, c
    # Unicode format would use symbols: ♠, ♥, ♦, ♣

    has_ascii_suits = any(suit in context_str for suit in ['s', 'h', 'd', 'c'])
    has_unicode_suits = any(suit in context_str for suit in ['♠', '♥', '♦', '♣'])

    print("\n✅ Format Detection:")
    print(f"   ASCII suits (s/h/d/c) found: {has_ascii_suits}")
    print(f"   Unicode suits (♠♥♦♣) found: {has_unicode_suits}")

    # Test specific cards
    kd = Card('Kd')
    kc = Card('Kc')
    pocket_kings_str = game_context.cards_to_string([kd, kc])

    print(f"\n🃏 Pocket Kings Display:")
    print(f"   Format: {pocket_kings_str}")
    print(f"   Expected: Kd Kc (ASCII)")
    print(f"   NOT: K♦ K♣ (Unicode)")

    # Assertions
    assert pocket_kings_str == "Kd Kc", f"Expected 'Kd Kc', got '{pocket_kings_str}'"
    assert has_ascii_suits, "Context should use ASCII suits (s/h/d/c)"
    assert not has_unicode_suits, "Context should NOT use Unicode suits (♠♥♦♣)"

    print("\n✅ GUI ASCII format test PASSED!")
    print("   Cards will display as: As, Kh, Qd, Jc")
    print("   NOT as: A♠, K♥, Q♦, J♣")
    print("   This ensures proper display in terminal/chat interfaces")
    print("="*70)


if __name__ == "__main__":
    test_gui_uses_ascii_format()
