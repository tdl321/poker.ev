#!/usr/bin/env python3
"""
Test poker.ev components

This script tests the core components to ensure everything is working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        from poker_ev.engine.game_wrapper import PokerGame
        print("  ✓ PokerGame imported")

        from poker_ev.gui.card_renderer import CardRenderer
        print("  ✓ CardRenderer imported")

        from poker_ev.gui.event_handler import EventHandler
        print("  ✓ EventHandler imported")

        from poker_ev.agents.agent_manager import AgentManager
        print("  ✓ AgentManager imported")

        from poker_ev.gui.pygame_gui import PygameGUI
        print("  ✓ PygameGUI imported")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_game_wrapper():
    """Test PokerGame wrapper"""
    print("\nTesting PokerGame wrapper...")

    try:
        from poker_ev.engine.game_wrapper import PokerGame

        # Create game
        game = PokerGame(num_players=3, buyin=1000, big_blind=10, small_blind=5)
        print("  ✓ Game created")

        # Start hand
        game.start_new_hand()
        print("  ✓ Hand started")

        # Get state
        state = game.get_game_state()
        assert state['hand_active'] == True
        assert len(state['players']) == 3
        assert state['pot'] > 0  # Should have blinds
        print(f"  ✓ Game state retrieved (pot: ${state['pot']})")

        # Check players have cards
        human_player = state['players'][0]
        assert len(human_player['hand']) == 2
        print(f"  ✓ Players have cards")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_card_renderer():
    """Test CardRenderer"""
    print("\nTesting CardRenderer...")

    try:
        import sys
        sys.path.insert(0, './texasholdem')

        from texasholdem import Card
        from poker_ev.gui.card_renderer import CardRenderer

        # Create mock sprites dictionary
        card_sprites = {
            "AS": "mock_sprite",
            "KD": "mock_sprite",
            "back_red": "mock_sprite"
        }

        renderer = CardRenderer(card_sprites)
        print("  ✓ CardRenderer created")

        # Test card conversion
        card = Card("As")
        sprite_name = renderer.card_to_sprite_name(card)
        assert sprite_name == "AS"
        print(f"  ✓ Card conversion works: Card('As') → '{sprite_name}'")

        # Test more cards
        test_cases = [
            (Card("Kd"), "KD"),
            (Card("2h"), "2H"),
            (Card("Tc"), "10C"),  # T = 10 in card notation
        ]

        for card, expected in test_cases:
            result = renderer.card_to_sprite_name(card)
            assert result == expected, f"Expected {expected}, got {result}"

        print(f"  ✓ All card conversions correct")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_manager():
    """Test AgentManager"""
    print("\nTesting AgentManager...")

    try:
        import sys
        sys.path.insert(0, './texasholdem')

        from texasholdem import TexasHoldEm, ActionType
        from poker_ev.agents.agent_manager import AgentManager

        # Create manager
        manager = AgentManager()
        print("  ✓ AgentManager created")

        # Register agents
        manager.register_agent(1, AgentManager.random_agent)
        manager.register_agent(2, AgentManager.call_agent)
        print("  ✓ Agents registered")

        # Create test game
        game = TexasHoldEm(buyin=1000, big_blind=10, small_blind=5, max_players=3)
        game.start_hand()

        # Get action from agent
        action, amount = manager.get_action(game, 1)
        assert isinstance(action, ActionType)
        print(f"  ✓ Agent returned action: {action}")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("poker.ev Component Tests")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("PokerGame", test_game_wrapper()))
    results.append(("CardRenderer", test_card_renderer()))
    results.append(("AgentManager", test_agent_manager()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20} {status}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All tests passed! Ready to run poker.ev!")
        print("\nRun the game with:")
        print("  python3 main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
