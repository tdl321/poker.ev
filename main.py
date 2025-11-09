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
    print("  • Player 1: Call Agent (always calls)")
    print("  • Player 2: Random Agent")
    print("  • Player 3: Aggressive Agent (raises often)")
    print("  • Player 4: Tight Agent (folds often)")
    print("  • Player 5: Random Agent")
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
    # Assign different AI strategies to other players
    agent_manager.register_agent(1, AgentManager.call_agent)
    agent_manager.register_agent(2, AgentManager.random_agent)
    agent_manager.register_agent(3, AgentManager.aggressive_agent)
    agent_manager.register_agent(4, AgentManager.tight_agent)
    agent_manager.register_agent(5, AgentManager.random_agent)

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
