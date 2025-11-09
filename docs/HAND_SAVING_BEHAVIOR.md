# Hand Saving Behavior - How Data is Stored in Pinecone

## Overview

The poker application stores two types of data in the `poker-memory` Pinecone index:
1. **Decision Records** (pre-decision and post-decision) - saved in real-time during play
2. **Full Hand Records** - saved when a hand ends

This document explains when each type is saved and how the LLM uses them.

## Data Types

### 1. Decision Records (Real-time)

**Pre-Decision Records:**
- Saved BEFORE the player acts
- Contains: cards, position, pot, chips to call, board state
- Type: `pre_decision`
- ID format: `pre_decision_{hand_id}_{counter}`

**Post-Decision Records:**
- Saved AFTER the player acts
- Contains: action taken, amount, result
- Type: `post_decision`
- ID format: `post_decision_{hand_id}_{counter}`

**When they're saved:**
- Pre-decision: When player clicks a button (CALL, FOLD, RAISE)
- Post-decision: Immediately after action is executed successfully

**Purpose:**
- Enable LLM to search past decisions: "What did I do in similar situations?"
- Track decision patterns over time
- Provide real-time advice based on similar past spots

### 2. Full Hand Records (End of hand)

**Full Hand Records:**
- Saved when hand ENDS (hand_active transitions to False)
- Contains: cards, board, pot, outcome (won/lost/folded/push), profit
- Type: `hand`
- ID format: `hand_{timestamp}`

**When they're saved:**
- Normal: When hand ends naturally
- Incomplete: When player quits mid-hand (marked as 'incomplete')

**Purpose:**
- Post-game analysis
- Pattern recognition across hands
- Historical win/loss tracking

## Timeline Example

```
1. Hand starts (hand_1762672402)
   └─ Decision tracking initialized
   └─ Full hand NOT yet saved ❌

2. Player is deciding what to do
   └─ Pre-decision saved ✓
   └─ Full hand still NOT saved ❌

3. Player clicks CALL
   └─ Post-decision saved ✓
   └─ Full hand still NOT saved ❌

4. Hand ends (player wins)
   └─ Full hand saved ✓
   └─ Decision outcomes updated ✓
```

## Common Scenarios

### Scenario 1: Current Active Hand

**User asks: "What's the best move for my current hand?"**

- LLM should use `get_game_state()` to see CURRENT cards/board
- Does NOT query Pinecone for this hand (it's not saved yet)
- MAY query Pinecone for similar PAST decisions
- ✅ Our fix ensures LLM uses current game state, not past hands

### Scenario 2: User Quits Mid-Hand

**What happens:**
- If hand is active when game exits
- `_save_incomplete_hand_on_exit()` is called
- Hand is saved with outcome='incomplete'
- This prevents data loss

### Scenario 3: User Folds Pre-Flop

**What happens:**
- Pre-decision was saved ✓
- Player clicks FOLD
- Post-decision is saved ✓
- Hand ends immediately
- Full hand is saved with outcome='folded' ✓

## Why This Design?

### Decision Records are Saved Immediately

**Pros:**
- Available for LLM queries during the hand
- Can ask "what did I do last time I had pocket aces?"
- No data loss if game crashes

**Cons:**
- More database writes
- Incomplete if hand doesn't finish

### Full Hands are Saved at End

**Pros:**
- Complete picture of entire hand
- Accurate profit/loss calculation
- Clean data (no partial hands)

**Cons:**
- Not available until hand completes
- Can be lost if game crashes (now fixed with incomplete hand saving)

## Database Queries

### For Current Hand Advice

```python
# DON'T do this - it won't find the current hand!
results = search_past_decisions("pocket aces on button")

# DO this - get current state first
current_state = game_context_provider.get_full_context()
# Then optionally search past similar situations
```

### For Learning from History

```python
# This is correct - query past decisions
results = search_past_decisions("pocket jacks facing raise")
# Returns: similar situations from PAST hands, with their outcomes
```

## Troubleshooting

### "Current hand not in database"

**This is expected!** Current active hands are NOT in Pinecone yet.

- Use `get_game_state()` for current hand data
- Pinecone is for PAST hands only

### "Hands with pre-decisions but no full hand record"

**Possible causes:**
1. ✅ **FIXED**: Game exited before hand ended → now saves as 'incomplete'
2. Player is still in the hand (check if hand is active)
3. Hand-end logic didn't trigger (check logs for "Hand ended" message)

### "Pre-decisions saved but no post-decisions"

**Possible causes:**
1. Player canceled the action (e.g., clicked RAISE then canceled)
2. Action failed to execute
3. Decision tracking was disabled mid-hand

## Key Takeaway

**For the LLM:**
- Current hand → use `get_game_state()` ✓
- Past similar hands → query Pinecone ✓
- NEVER confuse current hand with past hands ✓ (fixed with enhanced system prompt + injected context)

**For developers:**
- Decision records = real-time during hand
- Full hand records = saved at end
- Incomplete hands now saved on exit
