#!/usr/bin/env python3
"""
poker.ev - AI Poker Application

Main entry point for the application.
Combines texasholdem's production-ready engine with pyker's beautiful UI.
"""

import sys
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.gui.pygame_gui import PygameGUI
from poker_ev.agents.agent_manager import AgentManager


def main():
    """
    Run the poker.ev application

    This creates a 6-player game where:
    - Player 0 is human (you)
    - Players 1-5 are AI opponents with different strategies
    """

    print("=" * 60)
    print("Welcome to poker.ev - AI Poker Application!")
    print("=" * 60)
    print()
    print("Game Setup:")
    print("  • 6 players total")
    print("  • You are Player 0 (bottom of table)")
    print("  • Starting chips: $1000")
    print("  • Blinds: $5 / $10")
    print()
    print("Controls:")
    print("  • Click action buttons to play")
    print("  • Keyboard shortcuts:")
    print("    - F: Fold")
    print("    - C: Call/Check")
    print("    - R: Raise")
    print("    - A: All In")
    print("    - Tab: Toggle AI advisor panel")
    print("    - ESC: Cancel raise")
    print()
    print("Features:")
    print("  • AI Poker Advisor with RAG (press Tab)")
    print("  • Automatic hand history saving to Pinecone")
    print("  • Semantic search for similar hands")
    print()
    print("AI Opponents:")
    print("  • 5 Neural Network agents with varying risk profiles")
    print("    - Risk-seeking (aggressive play)")
    print("    - Risk-neutral (balanced play)")
    print("    - Risk-averse (conservative play)")
    print("  • Random mix each game for variety")
    print()
    print("=" * 60)
    print("Starting game...")
    print("=" * 60)
    print()

    # Create game
    game = PokerGame(
        num_players=6,
        buyin=1000,
        big_blind=10,
        small_blind=5
    )

    # Setup AI agents
    agent_manager = AgentManager()

    # Player 0 is human (no agent)
    # Try to setup neural network agents, fall back to rule-based if unavailable
    use_neural_agents = os.getenv('USE_NEURAL_AGENTS', 'true').lower() == 'true'
    verbose_agents = os.getenv('VERBOSE_AGENTS', 'false').lower() == 'true'

    if use_neural_agents:
        try:
            print("🧠 Loading neural network agents...")
            agent_manager.setup_neural_agents(
                num_players=6,
                human_player=0,
                verbose=verbose_agents
            )
            print("✓ Neural agents loaded successfully!\n")
        except Exception as e:
            print(f"⚠ Warning: Could not load neural agents: {e}")
            print("   Falling back to rule-based agents...\n")
            use_neural_agents = False

    if not use_neural_agents:
        print("🎮 Using rule-based agents:")
        print("  • Player 1: Call Agent")
        print("  • Player 2: Random Agent")
        print("  • Player 3: Aggressive Agent")
        print("  • Player 4: Tight Agent")
        print("  • Player 5: Random Agent\n")
        agent_manager.setup_default_agents(num_players=6, human_player=0)

    # Create and run GUI
    try:
        # Set enable_chat=True to enable AI poker advisor
        gui = PygameGUI(game, agent_manager, enable_chat=True)
        gui.run()
    except Exception as e:
        print(f"\nError running game: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\nThanks for playing poker.ev!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
