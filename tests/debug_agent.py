#!/usr/bin/env python3
"""Debug script to see full agent response structure"""

import os
import sys
from dotenv import load_dotenv
import logging

# Load .env
load_dotenv()

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_ev.llm.poker_advisor import PokerAdvisor

logging.basicConfig(level=logging.WARNING)

print("Initializing poker advisor...")
advisor = PokerAdvisor()

print("\n" + "="*60)
print("Testing: Should I call with pocket jacks?")
print("="*60)

result = advisor.agent.invoke({
    "messages": [{"role": "user", "content": "Should I call with pocket jacks?"}]
})

print(f"\nResult type: {type(result)}")
print(f"Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

if "messages" in result:
    print(f"\nTotal messages: {len(result['messages'])}")

    for i, msg in enumerate(result["messages"]):
        print(f"\n--- Message {i} ---")
        print(f"Type: {type(msg)}")
        print(f"Has content: {hasattr(msg, 'content')}")

        if hasattr(msg, "content"):
            content = msg.content
            print(f"Content type: {type(content)}")
            print(f"Content length: {len(str(content))}")
            print(f"Content preview: {str(content)[:200]}")

        if hasattr(msg, "tool_calls"):
            print(f"Tool calls: {msg.tool_calls}")

        if hasattr(msg, "role"):
            print(f"Role: {msg.role}")

print("\n" + "="*60)
print("Using get_advice method:")
print("="*60)
advice = advisor.get_advice("Should I call with pocket jacks?")
print(f"\nAdvice: {advice}")
