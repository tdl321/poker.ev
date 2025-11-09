#!/usr/bin/env python3
"""
poker.ev - AI Poker Application (DEBUG MODE)

This is a debug-enabled version that shows Pinecone storage in action.
- Logs when hands are saved to Pinecone
- Shows storage status in console
- Displays hand data being stored
"""

import sys
import os
import logging

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.gui.pygame_gui import PygameGUI
from poker_ev.agents.agent_manager import AgentManager
from poker_ev.memory.hand_history import HandHistory
from poker_ev.memory.pinecone_store import PineconeMemoryStore


def main():
    """
    Run the poker.ev application with DEBUG mode enabled
    """

    print("=" * 70)
    print("🐛 poker.ev - DEBUG MODE")
    print("=" * 70)
    print()
    print("This version includes:")
    print("  ✓ Detailed console logging")
    print("  ✓ Automatic hand saving to Pinecone")
    print("  ✓ Storage verification after each hand")
    print("  ✓ Debug overlay in GUI")
    print()
    print("=" * 70)
    print()

    # Initialize Pinecone connection first
    print("🔌 Connecting to Pinecone...")
    try:
        hand_history = HandHistory()
        print("✅ Pinecone connection successful!")
        print(f"   Using index: poker-memory")
        print()
    except Exception as e:
        print(f"❌ Failed to connect to Pinecone: {e}")
        print()
        print("Make sure you have PINECONE_API_KEY set in .env file")
        return 1

    print("=" * 70)
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
    print("    - D: Toggle debug overlay (shows Pinecone status)")
    print("    - ESC: Cancel raise")
    print()
    print("AI Opponents:")
    print("  • Player 1: Call Agent (always calls)")
    print("  • Player 2: Random Agent")
    print("  • Player 3: Aggressive Agent (raises often)")
    print("  • Player 4: Tight Agent (folds often)")
    print("  • Player 5: Random Agent")
    print()
    print("=" * 70)
    print("Starting game...")
    print("=" * 70)
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

    # Create and run GUI with debug mode
    try:
        # Set enable_chat=True to enable AI poker advisor
        gui = PygameGUI(
            game,
            agent_manager,
            enable_chat=True,
            debug_mode=True,  # Enable debug overlay
            hand_history=hand_history  # Pass hand_history for auto-saving
        )
        gui.run()
    except TypeError:
        # If GUI doesn't support debug_mode yet, fall back to regular mode
        print("⚠️  GUI doesn't support debug_mode parameter yet")
        print("   Running in regular mode with manual logging...")
        print()

        from poker_ev.gui.pygame_gui_debug import PygameGUIDebug
        gui = PygameGUIDebug(
            game,
            agent_manager,
            enable_chat=True,
            hand_history=hand_history
        )
        gui.run()
    except Exception as e:
        print(f"\nError running game: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 70)
    print("Thanks for playing poker.ev!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
