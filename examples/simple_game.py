"""
Simple poker.ev game example

This example shows how to create a basic poker game with AI opponents.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.gui.pygame_gui import PygameGUI
from poker_ev.agents.agent_manager import AgentManager


def main():
    """Run a simple 3-player game"""

    print("Simple Poker.ev Game")
    print("=" * 40)
    print("3 players: You vs 2 AI opponents")
    print()

    # Create a smaller 3-player game
    game = PokerGame(
        num_players=3,
        buyin=500,
        big_blind=5,
        small_blind=2
    )

    # Setup AI agents
    agent_manager = AgentManager()
    agent_manager.register_agent(1, AgentManager.random_agent)
    agent_manager.register_agent(2, AgentManager.call_agent)

    # Run game
    gui = PygameGUI(game, agent_manager, window_size=(1200, 800))
    gui.run()


if __name__ == "__main__":
    main()
