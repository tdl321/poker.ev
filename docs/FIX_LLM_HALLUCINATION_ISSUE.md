# Fix: LLM Hallucinating Wrong Cards from Vector Database

## Issue Description

The poker advisor LLM was giving advice based on **wrong card combinations** that didn't match the current game state. For example:

**Actual Game State:**
- Player has: A♣ K♦
- Flop: K♠ 4♣ 5♣
- This is a strong hand (top pair, top kicker)

**LLM Response (WRONG):**
```
"Based on your current situation:**Fold is the best move here.**You have 1♠ 9♠
on a 10♦ 2♦ 3♦ flop - this is a very weak hand with no pair, no draws, and
minimal equity."
```

The LLM was recommending folding a strong hand because it was analyzing completely different cards!

## Root Cause Analysis

After investigation, I found that:

1. **The agent IS calling tools correctly** - it calls `get_game_state()` to get current cards
2. **Two separate Pinecone indexes exist:**
   - `poker-knowledge` (58 vectors) - general poker strategy
   - `poker-memory` (8 vectors) - past hand histories with specific cards
3. **The agent also calls `search_past_decisions()`** - which queries the `poker-memory` index
4. **The LLM confuses past hands with current hands** - it sees cards from old hands in the vector DB results and uses those instead of the current game state

### Evidence

Running `debug_agent.py` showed:
- Message 1: Agent calls `get_game_state()` ✓
- Message 2: Returns "No active game state available" (when no game running)
- Message 3: Agent calls `search_past_decisions()`
- The search returns: "You have 3♠, J♥ in Button position..."
- **The LLM then uses these OLD cards instead of current state**

## The Fix

Implemented a **two-layer defense** to prevent this issue:

### Layer 1: Enhanced System Prompt

Updated `poker_ev/llm/poker_advisor.py:93-136` with a critical rule:

```python
CRITICAL RULE FOR CURRENT HAND ANALYSIS:
When analyzing the user's CURRENT hand:
1. ALWAYS call get_game_state() FIRST to see the current cards, board, and pot
2. The cards from get_game_state() are the ONLY cards you should use for advice
3. DO NOT use cards from search_past_decisions() - those are from PREVIOUS hands
4. search_past_decisions() is ONLY for learning from history, NOT for determining current cards
5. If get_game_state() returns "No active game state available", tell the user there's no active hand
```

### Layer 2: Inject Game State into Query

Modified `poker_ev/gui/pygame_gui.py:149-201` to detect when the user asks about their current hand and **prepend the current game state** to their message:

```python
# Detect current hand queries
current_hand_keywords = ['current', 'this hand', 'my hand', 'best move', 'should i', 'what do']

if any(keyword in message.lower() for keyword in current_hand_keywords):
    # Prepend current game state
    enhanced_message = f"""[CURRENT GAME STATE - Use ONLY these cards, not any from past hands]
{current_situation}

[USER QUERY]
{message}"""
```

This ensures the LLM sees the current game state **immediately and explicitly** in the user's message, making it much harder to confuse with past hands.

## How It Works Now

When user asks: "What is the best move for my current hand?"

**Before Fix:**
1. Agent calls `get_game_state()` → "You have A♣ K♦..."
2. Agent calls `search_past_decisions()` → "You have 1♠ 9♠..." (from old hand)
3. LLM gets confused, uses 1♠ 9♠ instead of A♣ K♦ ❌

**After Fix:**
1. Query is enhanced with: `[CURRENT GAME STATE] You have A♣ K♦ on K♠ 4♣ 5♣...`
2. Agent calls `get_game_state()` → confirms "You have A♣ K♦..."
3. System prompt explicitly says: "Use ONLY cards from get_game_state(), NOT from past hands"
4. LLM correctly uses A♣ K♦ for analysis ✓

## Testing

Run the test to verify the fix:

```bash
export PYTHONPATH=/Users/tdl321/Poker.ev:$PYTHONPATH
python tests/test_current_hand_advice.py
```

The response should:
- ✅ Use the correct cards from the current game state
- ✅ NOT mention random cards like "1♠ 9♠" or "10♦ 2♦ 3♦"
- ✅ Provide appropriate advice for the actual hand

## Files Modified

1. `poker_ev/llm/poker_advisor.py` - Enhanced system prompt with critical rule
2. `poker_ev/gui/pygame_gui.py` - Inject game state into queries about current hand

## Additional Notes

- The `poker-memory` index stores past hand histories for learning
- The `search_past_decisions()` tool is still useful for asking "what did I do in similar situations?"
- But it should NEVER override the current game state when giving advice
- This fix makes the distinction crystal clear to the LLM
