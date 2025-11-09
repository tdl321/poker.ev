"""
AI agents module

Manages AI opponents with different strategies, including:
- Rule-based agents (random, call, aggressive, tight)
- Neural network agents (trained with different risk profiles)
"""

from poker_ev.agents.agent_manager import AgentManager

__all__ = ['AgentManager']
