#!/usr/bin/env python3
"""
Test Expected Value (EV) calculation in poker_tools

This script demonstrates the new EV calculation feature.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from poker_ev.llm.poker_tools import PokerTools

print("=" * 80)
print("EXPECTED VALUE (EV) CALCULATION TEST")
print("=" * 80)

# Create poker tools
class MockPinecone:
    def search_as_context(self, query, k=2):
        return "Mock knowledge base"

tools_manager = PokerTools(
    pinecone_store=MockPinecone(),
    game_context_provider=None,
    decision_tracker=None,
    hand_history=None
)

tools = tools_manager.create_tools()

# Find the calculate_pot_odds tool
pot_odds_tool = None
for tool in tools:
    if tool.name == "calculate_pot_odds":
        pot_odds_tool = tool
        break

if not pot_odds_tool:
    print("❌ calculate_pot_odds tool not found!")
    sys.exit(1)

print("\n✅ Found calculate_pot_odds tool\n")

# Test cases
test_cases = [
    {
        "name": "Pot Odds Only (No EV)",
        "input": "100,25",
        "description": "$100 pot, $25 to call"
    },
    {
        "name": "Profitable Call (+EV)",
        "input": "100,25,35",
        "description": "$100 pot, $25 to call, 35% equity (above 20% required)"
    },
    {
        "name": "Unprofitable Call (-EV)",
        "input": "100,25,15",
        "description": "$100 pot, $25 to call, 15% equity (below 20% required)"
    },
    {
        "name": "Break-Even Call (0 EV)",
        "input": "100,25,20",
        "description": "$100 pot, $25 to call, 20% equity (exactly required)"
    },
    {
        "name": "Large Pot Profitable",
        "input": "500,50,25",
        "description": "$500 pot, $50 to call, 25% equity (above 9.1% required)"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'=' * 80}")
    print(f"TEST {i}: {test['name']}")
    print(f"Scenario: {test['description']}")
    print("=" * 80)

    result = pot_odds_tool.invoke(test['input'])
    print(result)

print("\n" + "=" * 80)
print("✅ ALL TESTS COMPLETE!")
print("=" * 80)

print("\n📝 Key Insights:")
print("• +EV calls are profitable in the long run")
print("• -EV calls lose money over time")
print("• 0 EV calls break even")
print("• Higher equity vs required equity = more profitable")
print("• ROI shows return on investment percentage")
