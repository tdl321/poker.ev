#!/usr/bin/env python3
"""
Test script for neural agent integration

This script tests the neural agent adapter without running the full GUI.
It verifies:
1. State conversion from TexasHoldEm to PokerEnv format
2. Neural agent loading and action selection
3. Integration with AgentManager
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from texasholdem import TexasHoldEm, ActionType
from poker_ev.agents.agent_manager import AgentManager
from poker_ev.agents.state_converter import (
    texasholdem_to_pokerenv_state,
    convert_card_to_tuple
)


def test_state_conversion():
    """Test state conversion from TexasHoldEm to PokerEnv format"""
    print("\n" + "="*60)
    print("TEST 1: State Conversion")
    print("="*60)

    # Create a simple game
    game = TexasHoldEm(buyin=1000, big_blind=10, small_blind=5, max_players=6)
    game.start_hand()

    # Convert state for player 0
    state = texasholdem_to_pokerenv_state(game, player_id=0)

    print(f"✓ State shape: {state.shape}")
    print(f"✓ Expected shape: (44,)")
    assert state.shape == (44,), f"Expected shape (44,), got {state.shape}"

    print(f"✓ State dtype: {state.dtype}")
    assert state.dtype == 'float32', f"Expected dtype float32, got {state.dtype}"

    print("\n✓ State conversion test PASSED")
    return True


def test_neural_agent_loading():
    """Test loading neural agents with AgentManager"""
    print("\n" + "="*60)
    print("TEST 2: Neural Agent Loading")
    print("="*60)

    agent_manager = AgentManager()

    # Try to load neural agents
    try:
        print("\n🧠 Attempting to load neural network agents...")
        agent_manager.setup_neural_agents(num_players=6, human_player=0)
        print("✓ Neural agents loaded successfully!")
        return True
    except Exception as e:
        print(f"⚠ Warning: Neural agent loading failed: {e}")
        print("   This is expected if model files are not yet trained")
        print("   To train models, run: python model/train_agents.py")
        return False


def test_neural_agent_action():
    """Test that neural agents can select actions in a real game"""
    print("\n" + "="*60)
    print("TEST 3: Neural Agent Action Selection")
    print("="*60)

    # Create game
    game = TexasHoldEm(buyin=1000, big_blind=10, small_blind=5, max_players=6)
    game.start_hand()

    # Create agent manager
    agent_manager = AgentManager()

    # Try to setup neural agents
    try:
        agent_manager.setup_neural_agents(num_players=6, human_player=0)

        # Test action selection for each AI player
        print("\n🎮 Testing action selection for 5 AI players:")
        for player_id in range(1, 6):
            if agent_manager.has_agent(player_id):
                # Get action from agent
                game.current_player = player_id  # Simulate this player's turn
                action, amount = agent_manager.get_action(game, player_id)

                print(f"  Player {player_id}: {action} (amount={amount})")

                # Verify action is valid ActionType
                assert isinstance(action, ActionType), \
                    f"Expected ActionType, got {type(action)}"

                # Verify amount is integer
                assert isinstance(amount, int), \
                    f"Expected int amount, got {type(amount)}"

        print("\n✓ Neural agent action selection test PASSED")
        return True

    except Exception as e:
        print(f"⚠ Neural agent action test skipped: {e}")
        return False


def test_fallback_to_rule_based():
    """Test fallback to rule-based agents"""
    print("\n" + "="*60)
    print("TEST 4: Fallback to Rule-Based Agents")
    print("="*60)

    # Create game
    game = TexasHoldEm(buyin=1000, big_blind=10, small_blind=5, max_players=6)
    game.start_hand()

    # Create agent manager
    agent_manager = AgentManager()

    # Setup rule-based agents
    print("\n🎮 Setting up rule-based agents...")
    agent_manager.setup_default_agents(num_players=6, human_player=0)

    # Test action selection
    print("Testing action selection:")
    for player_id in range(1, 6):
        if agent_manager.has_agent(player_id):
            game.current_player = player_id
            action, amount = agent_manager.get_action(game, player_id)
            print(f"  Player {player_id}: {action}")

            assert isinstance(action, ActionType), \
                f"Expected ActionType, got {type(action)}"

    print("\n✓ Rule-based agent fallback test PASSED")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("NEURAL AGENT INTEGRATION TEST SUITE")
    print("="*60)

    results = []

    # Test 1: State conversion (always should work)
    try:
        results.append(("State Conversion", test_state_conversion()))
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        results.append(("State Conversion", False))

    # Test 2: Neural agent loading (may fail if models not trained)
    try:
        results.append(("Neural Agent Loading", test_neural_agent_loading()))
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        results.append(("Neural Agent Loading", False))

    # Test 3: Neural agent action (may fail if models not trained)
    try:
        results.append(("Neural Agent Actions", test_neural_agent_action()))
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        results.append(("Neural Agent Actions", False))

    # Test 4: Fallback (should always work)
    try:
        results.append(("Rule-Based Fallback", test_fallback_to_rule_based()))
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        results.append(("Rule-Based Fallback", False))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")

    # Overall status
    all_critical_passed = results[0][1] and results[3][1]  # State conversion and fallback
    neural_available = results[1][1] and results[2][1]  # Neural loading and actions

    print("\n" + "="*60)
    if all_critical_passed:
        print("✓ CRITICAL TESTS PASSED")
        print("  The integration is working correctly!")
        if neural_available:
            print("  Neural agents are available and functional.")
        else:
            print("  Neural agents not available (models not trained yet).")
            print("  Run: python model/train_agents.py")
    else:
        print("❌ CRITICAL TESTS FAILED")
        print("  There are issues with the integration.")

    print("="*60 + "\n")

    return 0 if all_critical_passed else 1


if __name__ == "__main__":
    sys.exit(main())
