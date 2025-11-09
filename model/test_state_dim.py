"""Quick test to determine the actual state dimension from PokerEnv."""

if __name__ == "__main__":
    from pokernew import PokerEnv

    # Create a simple environment
    env = PokerEnv(num_players=3, endowment=1000, small_blind=10, big_blind=20)

    # Suppress the dealing output by redirecting stdout temporarily
    import sys
    import io

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    env.deal(3)

    sys.stdout = old_stdout

    # Get state for player 0
    state = env.get_state(0)

    print(f"\n{'='*60}")
    print(f"STATE DIMENSION TEST")
    print(f"{'='*60}")
    print(f"State dimension: {len(state)}")
    print(f"State shape: {state.shape}")
    print(f"Sample state (first 30 elements): {state[:30]}")
    print(f"{'='*60}\n")
