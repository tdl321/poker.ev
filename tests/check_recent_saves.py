#!/usr/bin/env python3
"""Check what hands and decisions are actually in Pinecone"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from datetime import datetime

load_dotenv()

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")
index_name = "poker-memory"

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Get index stats
stats = index.describe_index_stats()
print("=" * 80)
print("POKER-MEMORY INDEX - RECENT SAVES")
print("=" * 80)
print(f"Total vectors: {stats.get('total_vector_count', 0)}")

# Query for recent saves
import numpy as np
dummy_vector = np.random.rand(384).tolist()

results = index.query(
    vector=dummy_vector,
    top_k=20,
    include_metadata=True
)

# Group by hand_id
hand_groups = {}
for match in results.get('matches', []):
    metadata = match.get('metadata', {})
    hand_id = metadata.get('hand_id', 'unknown')
    record_type = metadata.get('type', 'unknown')

    if hand_id not in hand_groups:
        hand_groups[hand_id] = {
            'hand_id': hand_id,
            'full_hand': [],
            'pre_decisions': [],
            'post_decisions': []
        }

    if record_type == 'hand':
        hand_groups[hand_id]['full_hand'].append(match)
    elif record_type == 'pre_decision':
        hand_groups[hand_id]['pre_decisions'].append(match)
    elif record_type == 'post_decision':
        hand_groups[hand_id]['post_decisions'].append(match)

# Sort by hand_id (timestamp-based)
sorted_hands = sorted(hand_groups.values(), key=lambda x: x['hand_id'], reverse=True)

print("\n" + "=" * 80)
print("RECENT HANDS (sorted by hand_id)")
print("=" * 80)

for i, hand_data in enumerate(sorted_hands[:10], 1):
    hand_id = hand_data['hand_id']
    print(f"\n{i}. Hand ID: {hand_id}")
    print(f"   Full hand saved: {'YES' if hand_data['full_hand'] else 'NO'}")
    print(f"   Pre-decisions: {len(hand_data['pre_decisions'])}")
    print(f"   Post-decisions: {len(hand_data['post_decisions'])}")

    # Show sample data
    if hand_data['full_hand']:
        full_hand = hand_data['full_hand'][0]['metadata']
        print(f"   └─ Cards: {full_hand.get('your_cards', 'N/A')}")
        print(f"      Outcome: {full_hand.get('outcome', 'N/A')}")
        print(f"      Profit: ${full_hand.get('profit', 0)}")

    if hand_data['pre_decisions']:
        pre = hand_data['pre_decisions'][0]['metadata']
        print(f"   └─ First decision: {pre.get('description', 'N/A')[:80]}...")

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)

# Check for hands with decisions but no full hand record
incomplete_hands = [h for h in sorted_hands if h['pre_decisions'] and not h['full_hand']]
if incomplete_hands:
    print(f"\n⚠️  Found {len(incomplete_hands)} hands with decisions but NO full hand record:")
    for h in incomplete_hands[:3]:
        print(f"   - {h['hand_id']}: {len(h['pre_decisions'])} pre, {len(h['post_decisions'])} post")
else:
    print("\n✅ All hands with decisions also have full hand records")

# Check for recent hand IDs (from logs: hand_1762672261, hand_1762672402)
print("\n" + "=" * 80)
print("CHECKING SPECIFIC HANDS FROM LOGS")
print("=" * 80)

log_hands = ['hand_1762672261', 'hand_1762672402']
for log_hand in log_hands:
    if log_hand in hand_groups:
        h = hand_groups[log_hand]
        print(f"\n{log_hand}:")
        print(f"  Full hand: {'SAVED' if h['full_hand'] else 'NOT SAVED'}")
        print(f"  Decisions: {len(h['pre_decisions'])} pre, {len(h['post_decisions'])} post")
    else:
        print(f"\n{log_hand}: NOT FOUND in database")
