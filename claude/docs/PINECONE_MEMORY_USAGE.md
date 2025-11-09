# Pinecone Memory Usage Guide

Complete guide to using the Pinecone-based memory system in Poker.ev

## Overview

The memory system now uses **Pinecone vector database** instead of SQLite for:
- **Hand History** - Store and semantically search past poker hands
- **Pattern Recognition** - Identify and track playing patterns
- **Session Management** - Remember past conversations and advice

## Benefits

### 1. Semantic Search
```python
# Instead of exact match queries:
history.get_hands_by_outcome("won")

# You can now do semantic search:
history.search_similar_hands("aggressive play against tight opponents", limit=5)
```

### 2. Pattern Recognition
Automatically find patterns across hands:
```python
tracker.discover_winning_patterns()
# Finds: "Profitable Button Play", "Aggressive Play Wins", etc.
```

### 3. Context-Aware Memory
The LLM can retrieve relevant past experiences:
```python
# Get similar hands for current situation
context = history.get_context_for_current_hand(current_hand, limit=3)
```

## Quick Start

### 1. Setup Pinecone API Key

Ensure your `.env` file has:
```bash
PINECONE_API_KEY=your-api-key-here
```

### 2. Initialize the Memory System

```python
from poker_ev.memory import PineconeMemoryStore, HandHistory, PatternTracker, SessionManager

# Option 1: Let each component create its own store
history = HandHistory()
tracker = PatternTracker()
manager = SessionManager()

# Option 2: Share a single Pinecone store (recommended)
store = PineconeMemoryStore()
history = HandHistory(pinecone_store=store)
tracker = PatternTracker(pinecone_store=store)
manager = SessionManager(pinecone_store=store)
```

### 3. Run Tests

```bash
python test_pinecone_memory.py
```

## Hand History

### Saving Hands

```python
from poker_ev.memory import HandHistory

history = HandHistory()

hand_data = {
    'hand_id': 'hand_001',
    'your_cards': ['A♠', 'K♥'],
    'board': ['Q♥', 'J♦', '10♣'],
    'actions_summary': 'Raised preflop, bet flop',
    'pot': 150,
    'outcome': 'won',
    'profit': 75,
    'phase': 'FLOP',
    'position': 'Button',
    'hand_strength': 'top pair',
    'board_texture': 'connected',
    'opponent_style': 'tight',
    'aggression_level': 'aggressive',
    'notes': 'Good value bet on flop'
}

history.save_hand(hand_data)
```

### Retrieving Hands

#### Recent Hands
```python
recent = history.get_recent_hands(limit=10)
for hand in recent:
    print(f"{hand['hand_id']}: {hand['outcome']} (${hand['profit']})")
```

#### Semantic Search
```python
# Find similar situations
similar = history.search_similar_hands(
    query="pocket aces against aggressive opponent",
    limit=5
)

for hand in similar:
    print(f"Similarity: {hand['similarity_score']:.3f}")
    print(f"Hand: {hand['your_cards']}")
    print(f"Outcome: {hand['outcome']}")
```

#### Filtered Search
```python
# Get winning hands from button
won_hands = history.search_similar_hands(
    query="winning hands from button",
    limit=10,
    filters={"outcome": "won", "position": "Button"}
)

# Get hands by position
button_hands = history.get_hands_by_position("Button", limit=20)

# Get hands by outcome
folded_hands = history.get_hands_by_outcome("folded", limit=20)
```

#### Context for Current Hand
```python
current_hand = {
    'your_cards': ['K♠', 'K♦'],
    'board': ['A♥', '7♦', '3♣'],
    'position': 'Big Blind'
}

# Get similar past hands
context = history.get_context_for_current_hand(current_hand, limit=3)

print("Similar situations from your history:")
for hand in context:
    print(f"  • {hand['your_cards']} on {hand['board']}")
    print(f"    Outcome: {hand['outcome']}, Profit: ${hand['profit']}")
```

### Statistics

```python
stats = history.get_statistics()
print(f"Total hands: {stats['total_hands']}")
print(f"Win rate: {stats['win_rate']}%")
print(f"Total profit: ${stats['total_profit']}")
print(f"Avg profit/hand: ${stats['avg_profit']}")
```

## Pattern Tracking

### Initialize Pattern Tracker

```python
from poker_ev.memory import PatternTracker, HandHistory

# Option 1: Create with shared hand history
history = HandHistory()
tracker = PatternTracker(hand_history=history)

# Option 2: Let it create its own
tracker = PatternTracker()
```

### Discover Patterns Automatically

```python
# Automatically find winning patterns
patterns = tracker.discover_winning_patterns(min_hands=5)

for pattern in patterns:
    print(f"Pattern: {pattern['pattern_name']}")
    print(f"Win Rate: {pattern['win_rate']}%")
    print(f"Frequency: {pattern['frequency']} hands")
    print(f"Insight: {pattern['insight']}")
```

### Identify Leaks

```python
leaks = tracker.identify_leaks()

print("Identified Issues:")
for i, leak in enumerate(leaks, 1):
    print(f"  {i}. {leak}")
```

### Search Patterns

```python
# Find patterns related to a topic
patterns = tracker.search_patterns("aggressive play from button", limit=5)

for pattern in patterns:
    print(f"Pattern: {pattern['pattern_name']}")
    print(f"Similarity: {pattern['similarity_score']:.3f}")
    print(f"Description: {pattern['description']}")
```

### Save Custom Patterns

```python
pattern_data = {
    'pattern_id': 'my_pattern_001',
    'pattern_name': 'Triple Barrel Bluff Success',
    'description': 'Successfully triple barreling with air on scary boards',
    'category': 'bluffing',
    'frequency': 8,
    'win_rate': 75.0,
    'success': True,
    'insight': 'Triple barreling works well against tight players on connected boards'
}

tracker.save_pattern(pattern_data)
```

### Analysis Report

```python
# Get comprehensive analysis
report = tracker.format_analysis_report()
print(report)
```

Output:
```
============================================================
PLAYER PATTERN ANALYSIS
============================================================

Overall Statistics:
  Total Hands: 150
  Win Rate: 52.0%
  Total Profit: $1250
  Avg Profit/Hand: $8.33

Aggression Factor:
  Style: Aggressive
  Factor: 2.5
  Raises: 45, Calls: 18

Win Rate by Position:
  Button: 65.0% (13/20 hands)
  Big Blind: 40.0% (8/20 hands)

Identified Issues:
  1. Low win rate in Early Position (25.0%). Consider tightening your opening range.
============================================================
```

## Session Management

### Create and Manage Sessions

```python
from poker_ev.memory import SessionManager

manager = SessionManager()

# Create new session
session_id = manager.create_session()

# Add messages
manager.add_message('user', 'Should I call with pocket jacks?')
manager.add_message('assistant', 'Pocket jacks are strong. Consider raising instead.')

# Save session
manager.save_session()
```

### Search Past Sessions

```python
# Find sessions about a topic
sessions = manager.search_sessions("pot odds calculations", limit=5)

for session in sessions:
    print(f"Session: {session['session_id']}")
    print(f"Similarity: {session['similarity_score']:.3f}")
    print(f"Summary: {session['summary']}")
    print(f"Topics: {session['topics']}")
```

### Get Past Advice

```python
# Retrieve advice given on a topic
advice = manager.get_past_advice_on_topic("bluffing strategies")

print("Past advice on bluffing:")
for adv in advice:
    print(f"  • {adv}")
```

### Export Conversations

```python
# Export to text
export = manager.export_conversation(format='txt')
print(export)

# Export to markdown
export = manager.export_conversation(format='md')
with open('conversation.md', 'w') as f:
    f.write(export)
```

## Advanced Usage

### Sharing a Single Pinecone Store

For efficiency, share one `PineconeMemoryStore` across all components:

```python
from poker_ev.memory import PineconeMemoryStore, HandHistory, PatternTracker, SessionManager

# Create shared store
store = PineconeMemoryStore()

# Initialize all components with shared store
history = HandHistory(pinecone_store=store)
tracker = PatternTracker(hand_history=history)  # Uses history's store
manager = SessionManager(pinecone_store=store)

# All components now use the same Pinecone connection
```

### Custom Index Settings

```python
store = PineconeMemoryStore(
    index_name="my-custom-poker-memory",  # Custom index name
    embedding_model="all-MiniLM-L6-v2",    # Embedding model
    dimension=384                           # Must match model
)
```

### Batch Operations

```python
# Save multiple hands efficiently
hands = [hand1, hand2, hand3, ...]

for hand in hands:
    history.save_hand(hand)

# Pinecone batches uploads automatically
```

### Complex Queries

```python
# Combine semantic search with filters
results = history.search_similar_hands(
    query="aggressive multiway pot with flush draw",
    limit=10,
    filters={
        "outcome": "won",
        "position": {"$in": ["Button", "Cutoff"]},
        "aggression_level": "aggressive"
    }
)
```

## Integration with LLM

### Building Context for AI Advisor

```python
def get_poker_advice(current_hand, question):
    """Get AI advice with memory context"""

    # Get relevant context from memory
    similar_hands = history.get_context_for_current_hand(current_hand, limit=3)
    relevant_patterns = tracker.search_patterns(question, limit=2)
    past_sessions = manager.search_sessions(question, limit=2)

    # Build context string
    context = "Relevant history:\n\n"

    context += "Similar hands you've played:\n"
    for hand in similar_hands:
        context += f"  • {hand['description']}\n"
        context += f"    Outcome: {hand['outcome']}, Profit: ${hand['profit']}\n"

    context += "\nRelevant patterns:\n"
    for pattern in relevant_patterns:
        context += f"  • {pattern['pattern_name']}: {pattern['insight']}\n"

    context += "\nPast discussions:\n"
    for session in past_sessions:
        context += f"  • {session['summary']}\n"

    # Pass context to LLM
    response = llm.chat(
        messages=[
            {"role": "system", "content": "You are a poker coach."},
            {"role": "user", "content": f"{context}\n\nCurrent situation: {question}"}
        ]
    )

    return response
```

## Monitoring & Maintenance

### Check Index Stats

```python
stats = store.get_stats()
print(f"Total vectors: {stats['total_vectors']}")
print(f"Index: {stats['index_name']}")
print(f"Dimension: {stats['dimension']}")
```

### View in Pinecone Dashboard

1. Go to https://app.pinecone.io/
2. Select your project
3. Click on `poker-memory` index
4. Browse vectors and test queries

## Cost & Limits

### Pinecone Free Tier
- **Storage:** 1 GB (enough for ~200K hands)
- **Queries:** Unlimited
- **Indexes:** 1 serverless index

### Current Usage
For a typical poker player:
- 1,000 hands × 1.5 KB/hand = **1.5 MB**
- 100 patterns × 0.5 KB = **50 KB**
- 100 sessions × 2 KB = **200 KB**

**Total: ~1.8 MB** - Well within free tier!

## Troubleshooting

### "No Pinecone API key found"
**Solution:** Add `PINECONE_API_KEY=...` to `.env` file

### "Failed to initialize Pinecone"
**Solution:**
1. Check API key is correct
2. Check internet connection
3. Verify Pinecone service status

### "Search returns no results"
**Solutions:**
1. Wait a few seconds after inserting data (Pinecone indexes asynchronously)
2. Check if data was actually saved
3. Try broader queries

### "Dimension mismatch"
**Solution:** Delete and recreate index with correct dimension, or use different embedding model

## Best Practices

1. **Share Pinecone Store** - Use one store across all components
2. **Wait After Insert** - Give Pinecone 1-2 seconds to index new data
3. **Use Descriptive Queries** - More context = better semantic search
4. **Add Rich Metadata** - Include `notes`, `actions_summary`, etc.
5. **Regular Cleanup** - Archive old data if approaching limits
6. **Test Queries** - Use Pinecone dashboard to test and refine queries

## Examples

See the test script for comprehensive examples:
```bash
python test_pinecone_memory.py
```

Or run individual component examples:
```bash
python poker_ev/memory/hand_history.py
python poker_ev/memory/pattern_tracker.py
python poker_ev/memory/session_manager.py
```

## Migration from SQLite

If you have existing SQLite data:

1. **Export SQLite data** to JSON
2. **Convert to Pinecone format** with proper metadata
3. **Batch insert** using `save_hand()`
4. **Verify** with test queries
5. **Remove** old SQLite database

Example migration script structure:
```python
import sqlite3
import json

# Read from SQLite
conn = sqlite3.connect('hand_history.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM hands')
rows = cursor.fetchall()

# Convert and save to Pinecone
history = HandHistory()
for row in rows:
    hand_data = convert_row_to_dict(row)
    history.save_hand(hand_data)
```

## Next Steps

1. ✅ Understand Pinecone memory architecture
2. ✅ Run test suite: `python test_pinecone_memory.py`
3. ✅ Integrate with your poker game
4. ✅ Start tracking hands and patterns
5. ✅ Leverage semantic search in AI advisor
6. ✅ Monitor usage and optimize queries

## Resources

- **Pinecone Docs:** https://docs.pinecone.io/
- **Design Document:** `claude/docs/PINECONE_MEMORY_DESIGN.md`
- **Setup Guide:** `claude/docs/PINECONE_SETUP.md`
- **Architecture:** `claude/docs/RAG_ARCHITECTURE.md`
