#!/usr/bin/env python3
"""Test chat functionality"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_ev.llm.poker_advisor import PokerAdvisor

print("Testing poker advisor chat...")
print("=" * 60)

advisor = PokerAdvisor()

# Test streaming
print("\nTesting streaming response:")
print("Q: What are pot odds?")
print("A: ", end='', flush=True)

for chunk in advisor.get_advice_stream("What are pot odds?"):
    print(chunk, end='', flush=True)

print("\n\n" + "=" * 60)
print("✅ Chat test complete!")
