"""
Test to verify the RAISE action fix for neural agents

This test simulates the scenario where a player has chips but not enough
to raise above the current bet, ensuring the agent doesn't get stuck in
an infinite loop.
"""

import sys
from pathlib import Path

# Add model directory to path
model_dir = Path(__file__).parent.parent / "model"
sys.path.insert(0, str(model_dir))

import torch
import numpy as np
from poker_agent import PokerAgent


class MockPokerEnv:
    """Mock PokerEnv for testing"""
    def __init__(self, player_money, player_bet, highest_bet, active=True):
        self.active_players = [active, True, True]
        self.bets = [player_bet, highest_bet, 0]
        self.money = [player_money, 1000, 1000]
        self.pot = sum(self.bets)


def test_raise_not_legal_when_no_chips_to_raise():
    """Test that RAISE is not legal when player can't raise above current bet"""
    print("Test 1: RAISE should be illegal when player has only enough to call")

    agent = PokerAgent(state_dim=44, hidden_dim=128, device='cpu')

    # Scenario: Player has 50 chips, current bet is 10, highest bet is 60
    # Player needs 50 chips to call, leaving 0 to raise
    env = MockPokerEnv(player_money=50, player_bet=10, highest_bet=60)
    player_id = 0

    legal_mask = agent.get_legal_actions(env, player_id)

    # Convert to list for readability
    legal_actions = [i for i, legal in enumerate(legal_mask) if legal]
    action_names = ['FOLD', 'CHECK', 'CALL', 'RAISE']
    legal_names = [action_names[i] for i in legal_actions]

    print(f"  Player money: {env.money[player_id]}")
    print(f"  Player bet: {env.bets[player_id]}")
    print(f"  Highest bet: {max(env.bets)}")
    print(f"  To call: {max(env.bets) - env.bets[player_id]}")
    print(f"  Legal actions: {legal_names}")

    # RAISE should NOT be legal (index 3)
    assert not legal_mask[3], "RAISE should not be legal when player can't raise"
    # CALL should be legal (index 2)
    assert legal_mask[2], "CALL should be legal"

    print("  ✓ PASS: RAISE correctly marked as illegal\n")


def test_raise_legal_when_chips_available():
    """Test that RAISE is legal when player has chips to raise"""
    print("Test 2: RAISE should be legal when player has chips to raise")

    agent = PokerAgent(state_dim=44, hidden_dim=128, device='cpu')

    # Scenario: Player has 100 chips, current bet is 10, highest bet is 60
    # Player needs 50 chips to call, leaving 50 to raise
    env = MockPokerEnv(player_money=100, player_bet=10, highest_bet=60)
    player_id = 0

    legal_mask = agent.get_legal_actions(env, player_id)

    legal_actions = [i for i, legal in enumerate(legal_mask) if legal]
    action_names = ['FOLD', 'CHECK', 'CALL', 'RAISE']
    legal_names = [action_names[i] for i in legal_actions]

    print(f"  Player money: {env.money[player_id]}")
    print(f"  Player bet: {env.bets[player_id]}")
    print(f"  Highest bet: {max(env.bets)}")
    print(f"  To call: {max(env.bets) - env.bets[player_id]}")
    print(f"  Legal actions: {legal_names}")

    # RAISE should be legal (index 3)
    assert legal_mask[3], "RAISE should be legal when player has chips to raise"

    print("  ✓ PASS: RAISE correctly marked as legal\n")


def test_get_raise_amount_returns_zero_when_no_chips():
    """Test that get_raise_amount returns 0 when player can't raise"""
    print("Test 3: get_raise_amount should return 0 when no chips to raise")

    agent = PokerAgent(state_dim=44, hidden_dim=128, device='cpu')

    # Scenario: Player has 50 chips, needs all 50 to call
    env = MockPokerEnv(player_money=50, player_bet=10, highest_bet=60)
    player_id = 0

    # Create dummy raise logits
    raise_logits = torch.randn(4)

    raise_amount = agent.get_raise_amount(env, player_id, raise_logits)

    print(f"  Player money: {env.money[player_id]}")
    print(f"  To call: {max(env.bets) - env.bets[player_id]}")
    print(f"  Raise amount: {raise_amount}")

    assert raise_amount == 0, f"Expected raise_amount=0, got {raise_amount}"

    print("  ✓ PASS: get_raise_amount correctly returns 0\n")


def test_consistency_between_legal_actions_and_raise_amount():
    """Test that if RAISE is illegal, get_raise_amount returns 0"""
    print("Test 4: Consistency check - if RAISE illegal, raise_amount should be 0")

    agent = PokerAgent(state_dim=44, hidden_dim=128, device='cpu')

    # Test multiple scenarios
    scenarios = [
        {"money": 50, "bet": 10, "highest": 60},  # No chips to raise
        {"money": 40, "bet": 0, "highest": 50},   # No chips to raise
        {"money": 100, "bet": 0, "highest": 0},   # Chips to raise
        {"money": 200, "bet": 50, "highest": 100}, # Chips to raise
    ]

    for i, scenario in enumerate(scenarios):
        env = MockPokerEnv(
            player_money=scenario["money"],
            player_bet=scenario["bet"],
            highest_bet=scenario["highest"]
        )
        player_id = 0

        legal_mask = agent.get_legal_actions(env, player_id)
        raise_logits = torch.randn(4)
        raise_amount = agent.get_raise_amount(env, player_id, raise_logits)

        raise_legal = legal_mask[3].item()

        print(f"  Scenario {i+1}: money={scenario['money']}, to_call={scenario['highest']-scenario['bet']}")
        print(f"    RAISE legal: {raise_legal}, raise_amount: {raise_amount}")

        # If RAISE is not legal, raise_amount should be 0
        if not raise_legal:
            assert raise_amount == 0, \
                f"Scenario {i+1}: RAISE illegal but raise_amount={raise_amount}"

    print("  ✓ PASS: All scenarios consistent\n")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing RAISE Action Fix for Neural Agent")
    print("=" * 70)
    print()

    try:
        test_raise_not_legal_when_no_chips_to_raise()
        test_raise_legal_when_chips_available()
        test_get_raise_amount_returns_zero_when_no_chips()
        test_consistency_between_legal_actions_and_raise_amount()

        print("=" * 70)
        print("All tests passed! ✓")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
