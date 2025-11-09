"""
Test to verify raise amount to total bet conversion in neural agent adapter

This test ensures that the neural agent correctly converts raise amounts
(how much to add on top of calling) to total bet amounts (what TexasHoldEm expects).
"""

import sys
from pathlib import Path

# Add directories to path
project_root = Path(__file__).parent.parent
model_dir = project_root / "model"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(model_dir))

import torch
from texasholdem import ActionType, PlayerState


# Mock classes to simulate the game state
class MockPlayer:
    """Mock player object"""
    def __init__(self, chips, state=PlayerState.IN):
        self.chips = chips
        self.state = state


class MockPot:
    """Mock pot object"""
    def __init__(self, amount):
        self.amount = amount


class MockGame:
    """Mock TexasHoldEm game for testing"""
    def __init__(self, num_players, player_chips, player_bets, min_raise_amount=10):
        self.players = [MockPlayer(chips) for chips in player_chips]
        self._player_bets = player_bets
        self.board = []
        self.pots = [MockPot(sum(player_bets))]
        self._min_raise = min_raise_amount

    def player_bet_amount(self, player_id):
        return self._player_bets[player_id]

    def get_available_moves(self):
        return [ActionType.FOLD, ActionType.CALL, ActionType.RAISE]

    def is_hand_running(self):
        return True

    def get_hand(self, player_id):
        """Return empty hand for testing"""
        return []

    def min_raise(self):
        """Return minimum raise amount"""
        return self._min_raise


def test_raise_amount_conversion():
    """Test that raise amount is correctly converted to total bet amount"""
    print("Test 1: Raise amount should be converted to total bet amount")

    from poker_ev.agents.neural_agent import NeuralAgentAdapter

    # Create a neural agent adapter (with untrained model for testing)
    adapter = NeuralAgentAdapter(
        model_path="nonexistent.pt",  # Will use untrained weights
        player_id=0,
        risk_profile='neutral'
    )

    # Scenario: Player 0 has bet 10, Player 1 has bet 60 (highest)
    # Player 0 wants to raise by 20 (from the neural network)
    # Expected total bet: 60 + 20 = 80
    game = MockGame(
        num_players=3,
        player_chips=[100, 50, 50],
        player_bets=[10, 60, 0]
    )

    # Mock the model's act method to return a specific raise amount
    def mock_act(state, env, player_id):
        action_idx = 3  # RAISE
        raise_amount = 20  # Want to raise by 20
        return action_idx, raise_amount, torch.zeros(4), 0.0

    # Replace the model's act method with our mock
    original_act = adapter.model.act
    adapter.model.act = mock_act

    try:
        # Call the adapter
        action, amount = adapter(game)

        print(f"  Player bets: {game._player_bets}")
        print(f"  Highest bet: {max(game._player_bets)}")
        print(f"  Neural network raise amount: 20")
        print(f"  Converted to total bet: {amount}")
        print(f"  Action: {action}")

        # Verify the conversion
        expected_total = 60 + 20  # highest_bet + raise_amount
        assert action == ActionType.RAISE, f"Expected RAISE, got {action}"
        assert amount == expected_total, f"Expected total={expected_total}, got {amount}"

        print(f"  ✓ PASS: Correctly converted raise amount 20 to total bet {expected_total}\n")

    finally:
        # Restore original method
        adapter.model.act = original_act


def test_raise_clipped_to_max_chips():
    """Test that total bet is clipped to player's available chips"""
    print("Test 2: Total bet should be clipped to player's available chips")

    from poker_ev.agents.neural_agent import NeuralAgentAdapter

    adapter = NeuralAgentAdapter(
        model_path="nonexistent.pt",
        player_id=0,
        risk_profile='neutral'
    )

    # Scenario: Player 0 has 100 chips, already bet 10, so has 90 left
    # Highest bet is 60, player wants to raise by 100
    # Expected total: min(60 + 100, 10 + 90) = min(160, 100) = 100
    game = MockGame(
        num_players=3,
        player_chips=[90, 50, 50],  # Remaining chips after current bet
        player_bets=[10, 60, 0]
    )

    def mock_act(state, env, player_id):
        return 3, 100, torch.zeros(4), 0.0  # Try to raise by 100

    original_act = adapter.model.act
    adapter.model.act = mock_act

    try:
        action, amount = adapter(game)

        print(f"  Player chips remaining: {game.players[0].chips}")
        print(f"  Player current bet: {game._player_bets[0]}")
        print(f"  Highest bet: {max(game._player_bets)}")
        print(f"  Neural network wants to raise by: 100")
        print(f"  Max total possible: {game._player_bets[0] + game.players[0].chips}")
        print(f"  Converted to total bet: {amount}")

        # Max total = current_bet + remaining_chips = 10 + 90 = 100
        expected_total = 100
        assert action == ActionType.RAISE, f"Expected RAISE, got {action}"
        assert amount == expected_total, f"Expected total={expected_total}, got {amount}"

        print(f"  ✓ PASS: Correctly clipped to max available chips\n")

    finally:
        adapter.model.act = original_act


def test_fallback_when_total_too_small():
    """Test that agent falls back to CALL when total bet would be <= highest bet"""
    print("Test 3: Should fall back to CALL when total bet <= highest bet")

    from poker_ev.agents.neural_agent import NeuralAgentAdapter

    adapter = NeuralAgentAdapter(
        model_path="nonexistent.pt",
        player_id=0,
        risk_profile='neutral'
    )

    # Scenario: Player has very few chips, can't actually raise
    # Player 0 has 5 chips, already bet 55, so max total = 60
    # Highest bet is 60, so can't raise
    game = MockGame(
        num_players=3,
        player_chips=[5, 50, 50],
        player_bets=[55, 60, 0]
    )

    def mock_act(state, env, player_id):
        return 3, 10, torch.zeros(4), 0.0  # Try to raise by 10

    original_act = adapter.model.act
    adapter.model.act = mock_act

    try:
        action, amount = adapter(game)

        print(f"  Player chips remaining: {game.players[0].chips}")
        print(f"  Player current bet: {game._player_bets[0]}")
        print(f"  Highest bet: {max(game._player_bets)}")
        print(f"  Neural network wants to raise by: 10")
        print(f"  Calculated total: {min(max(game._player_bets) + 10, game._player_bets[0] + game.players[0].chips)}")
        print(f"  Action taken: {action}")

        # Should fall back to CALL since total would be <= highest bet
        assert action in [ActionType.CALL, ActionType.CHECK], \
            f"Expected CALL or CHECK, got {action}"
        assert amount == 0, f"Expected amount=0 for {action}, got {amount}"

        print(f"  ✓ PASS: Correctly fell back to {action}\n")

    finally:
        adapter.model.act = original_act


def test_negative_raise_prevented():
    """Test that negative raise amounts are prevented"""
    print("Test 4: Negative raise amounts should trigger fallback")

    from poker_ev.agents.neural_agent import NeuralAgentAdapter

    adapter = NeuralAgentAdapter(
        model_path="nonexistent.pt",
        player_id=0,
        risk_profile='neutral'
    )

    game = MockGame(
        num_players=3,
        player_chips=[100, 50, 50],
        player_bets=[10, 60, 0]
    )

    def mock_act(state, env, player_id):
        return 3, -10, torch.zeros(4), 0.0  # Negative raise amount

    original_act = adapter.model.act
    adapter.model.act = mock_act

    try:
        action, amount = adapter(game)

        print(f"  Neural network returned raise amount: -10")
        print(f"  Action taken: {action}")

        # Should fall back to CALL/CHECK due to invalid raise amount
        assert action in [ActionType.CALL, ActionType.CHECK], \
            f"Expected CALL or CHECK for negative raise, got {action}"
        assert amount == 0, f"Expected amount=0, got {amount}"

        print(f"  ✓ PASS: Correctly fell back to {action} for negative raise\n")

    finally:
        adapter.model.act = original_act


def test_min_raise_requirement_met():
    """Test that raise amount is adjusted to meet minimum raise requirement"""
    print("Test 5: Raise amount should be adjusted to meet min_raise")

    from poker_ev.agents.neural_agent import NeuralAgentAdapter

    adapter = NeuralAgentAdapter(
        model_path="nonexistent.pt",
        player_id=0,
        risk_profile='neutral'
    )

    # Scenario: min_raise is 30, but neural net wants to raise by only 20
    # Should be adjusted to raise by 30 to meet minimum
    game = MockGame(
        num_players=3,
        player_chips=[100, 50, 50],
        player_bets=[10, 60, 0],
        min_raise_amount=30
    )

    def mock_act(state, env, player_id):
        return 3, 20, torch.zeros(4), 0.0  # Try to raise by 20

    original_act = adapter.model.act
    adapter.model.act = mock_act

    try:
        action, amount = adapter(game)

        print(f"  Highest bet: {max(game._player_bets)}")
        print(f"  Min raise: {game.min_raise()}")
        print(f"  Neural network wants to raise by: 20")
        print(f"  Expected total bet (to meet min): {max(game._player_bets) + game.min_raise()}")
        print(f"  Actual total bet: {amount}")
        print(f"  Action: {action}")

        # Should adjust to meet minimum raise requirement
        expected_total = 60 + 30  # highest_bet + min_raise
        assert action == ActionType.RAISE, f"Expected RAISE, got {action}"
        assert amount == expected_total, f"Expected total={expected_total}, got {amount}"

        print(f"  ✓ PASS: Correctly adjusted to meet min_raise requirement\n")

    finally:
        adapter.model.act = original_act


def test_min_raise_fallback_when_insufficient_chips():
    """Test that agent falls back to CALL when it can't meet min_raise"""
    print("Test 6: Should fall back to CALL when can't meet min_raise")

    from poker_ev.agents.neural_agent import NeuralAgentAdapter

    adapter = NeuralAgentAdapter(
        model_path="nonexistent.pt",
        player_id=0,
        risk_profile='neutral'
    )

    # Scenario: Player has 60 chips, bet 10 (50 remaining)
    # Highest bet is 40, so to_call = 30
    # After calling, player has 20 left
    # But min_raise is 30, so can't raise
    game = MockGame(
        num_players=3,
        player_chips=[50, 100, 100],  # 50 chips remaining
        player_bets=[10, 40, 0],
        min_raise_amount=30
    )

    def mock_act(state, env, player_id):
        return 3, 20, torch.zeros(4), 0.0  # Try to raise by 20

    original_act = adapter.model.act
    adapter.model.act = mock_act

    try:
        action, amount = adapter(game)

        print(f"  Player chips remaining: {game.players[0].chips}")
        print(f"  Player current bet: {game._player_bets[0]}")
        print(f"  Highest bet: {max(game._player_bets)}")
        print(f"  Min raise: {game.min_raise()}")
        print(f"  Chips available to raise: {game.players[0].chips - (max(game._player_bets) - game._player_bets[0])}")
        print(f"  Action: {action}")

        # Should fall back to CALL since can't meet min_raise
        assert action in [ActionType.CALL, ActionType.CHECK], \
            f"Expected CALL or CHECK, got {action}"
        assert amount == 0, f"Expected amount=0, got {amount}"

        print(f"  ✓ PASS: Correctly fell back to {action}\n")

    finally:
        adapter.model.act = original_act


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Raise Amount to Total Bet Conversion")
    print("=" * 70)
    print()

    try:
        test_raise_amount_conversion()
        test_raise_clipped_to_max_chips()
        test_fallback_when_total_too_small()
        test_negative_raise_prevented()
        test_min_raise_requirement_met()
        test_min_raise_fallback_when_insufficient_chips()

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
