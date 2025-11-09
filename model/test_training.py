"""Quick test to verify the training system works."""

import torch
from train_agents import MultiAgentPokerTrainer

if __name__ == "__main__":
    print("Testing Neural Network Poker Training System")
    print("=" * 60)

    # Configuration for quick test
    NUM_PLAYERS = 3
    ENDOWMENT = 1000
    STATE_DIM = 44  # Fixed state dimension
    HIDDEN_DIM = 64  # Smaller for faster testing
    LEARNING_RATE = 0.001
    NUM_EPISODES = 10  # Just a few episodes to test
    SMALL_BLIND = 10
    BIG_BLIND = 20

    print(f"Configuration:")
    print(f"  Players: {NUM_PLAYERS}")
    print(f"  Episodes: {NUM_EPISODES}")
    print(f"  State Dim: {STATE_DIM}")
    print("=" * 60)

    try:
        # Create trainer
        trainer = MultiAgentPokerTrainer(
            num_players=NUM_PLAYERS,
            endowment=ENDOWMENT,
            state_dim=STATE_DIM,
            hidden_dim=HIDDEN_DIM,
            lr=LEARNING_RATE,
            small_blind=SMALL_BLIND,
            big_blind=BIG_BLIND
        )

        # Train for a few episodes
        print("\nRunning test training...")
        trainer.train(num_episodes=NUM_EPISODES, print_every=5, verbose=False)

        print("\n" + "=" * 60)
        print("TEST PASSED: Training system works correctly!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
