# Pinecone Memory Design for Poker.ev

## Overview

Replace SQLite-based memory system with Pinecone vector database for semantic search and pattern recognition.

## Architecture

### Current System (SQLite)
```
HandHistory (SQLite)
    ↓
PatternTracker (queries SQLite)
    ↓
Basic pattern matching (exact queries)
```

### New System (Pinecone)
```
PineconeMemoryStore
    ↓
Semantic embeddings of hands, patterns, and sessions
    ↓
Smart retrieval via vector similarity
```

## Data Schema

### 1. Hand Memory Vectors

Each hand becomes a vector with rich metadata:

```python
{
    "id": "hand_20241108_001",
    "vector": [0.123, -0.456, ...],  # 384-dim embedding
    "metadata": {
        "hand_id": "20241108_001",
        "timestamp": "2024-11-08T14:30:00",
        "type": "hand",

        # Cards & Board
        "your_cards": "A♠ K♥",
        "board": "Q♥ J♦ 10♣ 9♠ 2♥",
        "hand_strength": "straight",

        # Actions
        "actions_summary": "Raised preflop, bet flop, called turn, bet river",
        "aggression_level": "aggressive",
        "phases_played": ["PREFLOP", "FLOP", "TURN", "RIVER"],

        # Outcome
        "outcome": "won",
        "pot": 150,
        "profit": 75,
        "position": "Button",

        # Context
        "opponent_style": "tight",
        "board_texture": "connected",

        # Semantic description
        "description": "Premium hand A-K, raised preflop from button against tight opponent. Made straight on flop, value bet and won 75 chips."
    }
}
```

**Embedding Source**: The `description` field creates the semantic vector.

### 2. Pattern Memory Vectors

Track recurring patterns across hands:

```python
{
    "id": "pattern_aggressive_button",
    "vector": [...],  # Embedding of pattern
    "metadata": {
        "pattern_id": "aggressive_button",
        "type": "pattern",
        "category": "position_play",

        # Pattern details
        "pattern_name": "Aggressive Button Play",
        "description": "Raising frequently from button position with wide range",
        "frequency": 15,  # Times observed
        "win_rate": 65.0,
        "avg_profit": 12.5,

        # Context
        "positions": ["Button"],
        "actions": ["RAISE", "BET"],
        "success": True,

        # Related hands
        "hand_ids": ["hand_001", "hand_015", "hand_023"],

        # Insights
        "insight": "Button aggression is very profitable - continue raising 70%+ of hands"
    }
}
```

### 3. Session Memory Vectors

Track chat conversations and advice given:

```python
{
    "id": "session_20241108_143000",
    "vector": [...],
    "metadata": {
        "session_id": "20241108_143000",
        "type": "session",
        "timestamp": "2024-11-08T14:30:00",

        # Conversation summary
        "summary": "Discussed pot odds calculation and when to call with flush draws",
        "topics": ["pot_odds", "flush_draws", "mathematics"],
        "advice_given": [
            "Need 4:1 odds for flush draw",
            "Consider implied odds with deep stacks"
        ],

        # Context
        "hands_discussed": ["hand_20241108_001"],
        "user_questions": [
            "What are pot odds?",
            "Should I call with a flush draw?"
        ],

        # Metadata
        "message_count": 12,
        "duration_minutes": 15
    }
}
```

### 4. Opponent Profile Vectors

```python
{
    "id": "opponent_player_3",
    "vector": [...],
    "metadata": {
        "opponent_id": 3,
        "type": "opponent_profile",
        "name": "Aggressive Agent",

        # Stats
        "vpip": 45,
        "pfr": 35,
        "aggression_factor": 3.5,

        # Tendencies
        "tendencies": "Raises 70% of the time, applies constant pressure, bluffs frequently",
        "exploits": "Call down lighter, trap with strong hands, let them bluff off chips",

        # Hand history
        "hands_played": 50,
        "hands_won": 18,
        "total_profit_against": -125,

        # Notable hands
        "key_hands": ["hand_020", "hand_035"]
    }
}
```

## Pinecone Indexes

### Option 1: Single Index (Recommended)
Use one index with metadata filtering:
- **Index Name**: `poker-memory`
- **Dimension**: 384
- **Metric**: Cosine
- **Filter by**: `metadata.type` (hand, pattern, session, opponent)

**Pros**: Simpler, cross-type semantic search possible
**Cons**: Need careful namespace management

### Option 2: Multiple Indexes
Separate indexes per type:
- `poker-hands` - Hand history
- `poker-patterns` - Pattern tracking
- `poker-sessions` - Chat sessions
- `poker-opponents` - Opponent profiles

**Pros**: Clean separation
**Cons**: More complex, higher cost

**Decision**: Use single index with metadata filtering.

## Query Patterns

### 1. Find Similar Hands
```python
query = "pocket jacks, raised preflop, opponent re-raised"
results = memory_store.search(
    query=query,
    filter={"type": "hand"},
    top_k=5
)
# Returns: 5 most similar hands from history
```

### 2. Identify Patterns
```python
query = "What patterns exist in my button play?"
results = memory_store.search(
    query=query,
    filter={"type": "pattern", "positions": {"$in": ["Button"]}},
    top_k=3
)
```

### 3. Recall Past Advice
```python
query = "previous discussions about flush draws"
results = memory_store.search(
    query=query,
    filter={"type": "session"},
    top_k=5
)
```

### 4. Find Opponent Patterns
```python
query = "aggressive opponent who bluffs frequently"
results = memory_store.search(
    query=query,
    filter={"type": "opponent_profile"},
    top_k=3
)
```

## Integration with LLM

### Enhanced Context Building

Before answering a user question:

1. **Semantic search** for relevant hands, patterns, sessions
2. **Build rich context** from retrieved memories
3. **Pass to LLM** with current game state

```python
async def get_advice(self, question: str, game_state: dict):
    # Search memory for context
    similar_hands = await self.memory.search(
        query=question,
        filter={"type": "hand"},
        top_k=3
    )

    similar_patterns = await self.memory.search(
        query=question,
        filter={"type": "pattern"},
        top_k=2
    )

    past_discussions = await self.memory.search(
        query=question,
        filter={"type": "session"},
        top_k=2
    )

    # Build context
    context = self._build_context(
        similar_hands,
        similar_patterns,
        past_discussions,
        game_state
    )

    # Get LLM response
    response = await self.llm.chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{context}\n\n{question}"}
        ]
    )

    return response
```

## Benefits

### 1. Semantic Pattern Recognition
- "Show me times I folded too early" → finds all hands where folding was suboptimal
- No need to manually tag or categorize

### 2. Cross-Domain Learning
- "How did I play against aggressive opponents?" → searches across hands, patterns, and sessions
- Connects insights from different data types

### 3. Temporal Patterns
- "Am I improving over time?" → compare early vs recent hands
- Track progression automatically

### 4. Context-Aware Advice
```
User: "Should I call with flush draw?"

Memory retrieval:
- Similar hand 3 days ago: folded flush draw, would have won
- Pattern: flush draws win 36% when pot odds are good
- Past session: discussed implied odds with flush draws

LLM response (with context):
"Based on your hand from Tuesday where you folded a flush draw that would have
won, and our previous discussion about implied odds, you should call here.
You're getting 3:1 pot odds, and your flush draw has ~36% equity..."
```

## Migration Strategy

### Phase 1: Dual System (Recommended)
- Keep SQLite for backwards compatibility
- Add Pinecone in parallel
- Gradually migrate queries to Pinecone

### Phase 2: Full Migration
- Once stable, remove SQLite
- Pure Pinecone system

## API Changes

### Old (SQLite)
```python
# Get recent hands
history.get_recent_hands(limit=10)

# Get hands by outcome
history.get_hands_by_outcome("won")

# Get statistics
history.get_statistics()
```

### New (Pinecone)
```python
# Get recent hands (still supported)
memory.get_recent_hands(limit=10)

# Semantic search for hands
memory.search_hands("winning hands with pocket pairs", top_k=10)

# Get patterns by query
memory.search_patterns("aggressive play from button", top_k=5)

# Smart statistics with context
memory.get_statistics(context="button play against tight opponents")
```

## Implementation Files

1. `poker_ev/memory/pinecone_store.py` - Main memory store
2. `poker_ev/memory/hand_history.py` - Update to use Pinecone
3. `poker_ev/memory/pattern_tracker.py` - Leverage semantic search
4. `poker_ev/memory/session_manager.py` - Store in Pinecone
5. `poker_ev/llm/poker_advisor.py` - Integrate memory retrieval

## Cost Considerations

### Free Tier
- 1 GB storage (enough for ~200K hands)
- Unlimited queries
- 1 serverless index

### Current Usage Estimate
- 40 documents (knowledge base) = 15 KB
- 1000 hands × 1.5 KB/hand = 1.5 MB
- 100 patterns × 0.5 KB = 50 KB
- 100 sessions × 2 KB = 200 KB

**Total: ~1.8 MB** - Well within free tier!

## Next Steps

1. Create `PineconeMemoryStore` class
2. Implement hand embedding and storage
3. Update `HandHistory` to use Pinecone
4. Update `PatternTracker` with semantic search
5. Integrate with `PokerAdvisor`
6. Test and validate performance
7. Documentation and examples
