# Decision-Action Tracking System - Complete Guide

## Overview

The Decision-Action Tracking System records **every poker decision** you make in two states:

1. **Pre-Decision State**: The situation BEFORE you act (your cards, pot size, opponents' actions, etc.)
2. **Post-Decision State**: The action you took and its immediate result
3. **Final Outcome**: Updated when the hand ends with the profit/loss

This creates a **chronological decision tree** that enables:
- **Real-time LLM advice** based on similar past situations
- **Post-game analysis** of decision optimality
- **Learning from patterns** in your play over time

---

## Architecture

### Two-Tier Tracking System

```
┌─────────────────────────────────────────────────────────────┐
│                        HAND STARTS                          │
│  DecisionTracker.start_hand(hand_id)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PLAYER'S TURN TO ACT                           │
│  • Cards: A♠ K♥                                            │
│  • Position: Button                                         │
│  • Pot: $150, To call: $20                                 │
│  • Opponent raised to $20                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            PRE-DECISION SAVE (BEFORE ACTION)                │
│  _save_pre_decision(state, pending_action)                 │
│                                                              │
│  Saves to Pinecone:                                         │
│  - decision_id: "decision_hand_12345_001"                  │
│  - type: "pre_decision"                                     │
│  - your_cards: ["A♠", "K♥"]                                │
│  - board: ["Q♥", "J♦", "10♣"]                             │
│  - pot: 150, chips_to_call: 20                             │
│  - position: "Button"                                       │
│  - description: "You have A♠, K♥ in Button position..."   │
│  - embedding: [0.23, -0.41, 0.87, ...] (384 dims)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               PLAYER TAKES ACTION                           │
│  User clicks "Raise to $60" button                         │
│  → game.take_action(ActionType.RAISE, 60)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           POST-DECISION SAVE (AFTER ACTION)                 │
│  _save_post_decision(action, amount)                       │
│                                                              │
│  Saves to Pinecone:                                         │
│  - decision_id: "decision_hand_12345_001" (same ID!)      │
│  - type: "post_decision"                                    │
│  - action: "raise"                                          │
│  - amount: 60                                               │
│  - chips_after: 930                                         │
│  - pot_after: 210                                           │
│  - hand_outcome: "" (empty until hand ends)                │
│  - description: "You raised to $60 with A♠ K♥..."         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         (More betting rounds...)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  HAND ENDS                                  │
│  _track_hand_end(state)                                    │
│                                                              │
│  Finalizes ALL decisions for this hand:                    │
│  - decision_tracker.finalize_hand_decisions(              │
│      hand_id="hand_12345",                                 │
│      outcome="won",                                         │
│      profit=135                                             │
│    )                                                        │
│                                                              │
│  Updates all post-decisions with outcome and profit        │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Schema

### Pre-Decision Record

Stored with vector ID: `pre_{decision_id}`

```python
{
  'decision_id': 'decision_hand_1699547823_001',
  'hand_id': 'hand_1699547823',
  'timestamp': '2025-01-08T15:24:13.123',
  'type': 'pre_decision',

  # Game situation
  'your_cards': '["A♠", "K♥"]',  # JSON string
  'board': '["Q♥", "J♦", "10♣"]',
  'phase': 'FLOP',
  'position': 'Button',

  # Financial state
  'your_chips': 990,
  'pot': 150,
  'chips_to_call': 20,
  'min_raise': 40,

  # Opponent information
  'previous_actions': '[{"player": 1, "action": "call"}, {"player": 2, "action": "raise", "amount": 20}]',
  'opponents': '[{"player_id": 1, "chips": 980, "bet": 20, "folded": false}, ...]',

  # Semantic description (what gets embedded)
  'description': 'You have A♠, K♥ in Button position. FLOP: Q♥, J♦, 10♣. Player 2 raise $20. Pot: $150. To call: $20. Your chips: $990'
}
```

**Vector Embedding**: 384-dimensional vector generated from `description` field using `all-MiniLM-L6-v2` model

### Post-Decision Record

Stored with vector ID: `post_{decision_id}`

```python
{
  'decision_id': 'decision_hand_1699547823_001',  # Same ID as pre-decision!
  'hand_id': 'hand_1699547823',
  'timestamp': '2025-01-08T15:24:15.456',
  'type': 'post_decision',

  # Links to pre-decision
  'pre_decision_id': 'decision_hand_1699547823_001',

  # Action taken
  'action': 'raise',
  'amount': 60,

  # Immediate result
  'chips_after': 930,  # 990 - 60
  'pot_after': 210,

  # Final outcome (updated when hand ends)
  'hand_outcome': 'won',        # won/lost/folded/push
  'hand_profit': 135,           # Net profit for the hand

  # Semantic description
  'description': 'You raised to $60 with A♠ K♥ in Button position facing a raise to $20'
}
```

---

## How the LLM Uses Decision History

### Real-Time Advice Flow

**User Scenario**: Has A♠ K♥ on Button, flop Q♥ J♦ 10♣, opponent raised to $20

```
1. User asks: "Should I call or raise?"

2. PokerAdvisor invokes tools:
   - get_game_state() → Gets current hand details
   - search_past_decisions("top pair top kicker on button facing raise on connected flop")

3. DecisionTracker searches Pinecone:
   - Embeds query: "top pair top kicker on button facing raise..."
   - Searches for similar pre_decision records
   - Returns top 3 matches with similarity scores

4. Results returned to LLM:

   Found 3 similar decisions from your past:

   1. Similarity: 0.89
      Situation: A♠, K♥ in Button
      Pot: $150, To call: $20
      Context: You have A♠, K♥ in Button position. FLOP: Q♥, 9♦, 2♣...
      (Check post-decision data for outcome)

   2. Similarity: 0.82
      Situation: A♦, Q♠ in Button
      Pot: $120, To call: $15
      Context: You have A♦, Q♠ in Button position. FLOP: Q♣, J♠, 8♥...

   3. Similarity: 0.78
      Situation: K♥, Q♥ in Cutoff
      Pot: $100, To call: $25
      ...

5. LLM combines:
   - Current game state
   - Similar past decisions
   - Poker strategy knowledge (from RAG)
   - Pot odds calculation

6. LLM responds:
   "Based on your history, you've been in similar spots 3 times with top pair.
    Looking at your past results, raising worked well when you had strong kickers.
    With A♠ K♥ giving you top pair top kicker plus a straight draw, I'd recommend
    raising to $60-80 here to build the pot and protect your hand."
```

---

## Code Integration Points

### 1. GUI Action Handling (`pygame_gui.py`)

**When user clicks action button:**

```python
def handle_action_click(self, action: ActionType):
    # Get current state
    state = self.game.get_game_state()

    # SAVE PRE-DECISION (BEFORE action)
    self._save_pre_decision(state, pending_action=action)

    # Execute action
    success = self.game.take_action(action, amount)

    if success:
        # SAVE POST-DECISION (AFTER action)
        self._save_post_decision(action, amount)
```

**For raises (two-step process):**

```python
# Step 1: User clicks RAISE button
def handle_action_click(self, ActionType.RAISE):
    self._save_pre_decision(state, pending_action=ActionType.RAISE)
    self.showing_raise_input = True  # Show slider

# Step 2: User confirms raise amount
def confirm_raise(self):
    success = self.game.take_action(ActionType.RAISE, self.raise_amount)
    if success:
        self._save_post_decision(ActionType.RAISE, self.raise_amount)
```

### 2. Decision Tracker (`decision_tracker.py`)

**Key Methods:**

```python
class DecisionTracker:
    def start_hand(self, hand_id: str):
        """Initialize tracking for a new hand"""

    def save_pre_decision(self, decision_id, game_state, your_cards, position, previous_actions):
        """Save state BEFORE player acts"""

    def save_post_decision(self, decision_id, action, amount, chips_after, pot_after):
        """Save action and immediate result"""

    def finalize_hand_decisions(self, hand_id, outcome, profit):
        """Update all decisions with final outcome"""

    def search_similar_decisions(self, query, decision_type='pre_decision', top_k=3):
        """Semantic search for similar past decisions"""
```

### 3. LLM Tool (`poker_tools.py`)

**New Tool:**

```python
@tool
def search_past_decisions(situation_description: str) -> str:
    """
    Search your past poker decisions for similar situations.

    Input: Description of current situation
    Returns: Similar past decisions with outcomes

    Example usage by LLM:
    - "What did I do with pocket jacks before?"
    - "How did I play top pair on the button?"
    """
    results = decision_tracker.search_similar_decisions(
        query=situation_description,
        decision_type='pre_decision',
        top_k=3
    )
    # Format and return results
```

---

## Usage Examples

### Example 1: Real-Time Advice

**During gameplay:**

```
Hand: A♠ K♥
Board: Q♥ J♦ 10♣
Opponent: Raised to $20
Pot: $150

User types in chat: "Should I raise or call?"

LLM Tool Invocations:
1. get_game_state() → "Your cards: A♠ K♥, Board: Q♥ J♦ 10♣..."
2. search_past_decisions("top pair button raise facing") → Returns 3 similar spots
3. calculate_pot_odds("150,20") → "Pot odds: 7.5:1, need 13.3% equity"

LLM Response:
"You have top pair with the best kicker plus a straight draw - very strong!
Your past history shows you raised in similar spots and won 67% of the time.
With this many outs (15+), raising to $60-80 is optimal to build the pot
and protect against draws."
```

### Example 2: Post-Game Review

**User asks:**

```
"Show me my last 5 decisions where I folded"

LLM uses: search_past_decisions() with filter: action="fold"

Returns:
1. Hand #1234: Folded K♥ Q♥ to $80 river bet - Would have won $200
2. Hand #1235: Folded 7♠ 7♦ to pre-flop 3-bet - Saved $40 (opponent had AA)
3. Hand #1236: Folded A♦ 8♦ on J♠ 9♣ 2♥ flop - Correct fold
...

LLM Analysis:
"You've folded 5 times recently. Hand #1234 was a bad fold - you had the flush
and should have called with 3.6:1 pot odds. Hand #1235 was a good fold against
a tight player's 3-bet. Overall, you're folding too much in late position."
```

### Example 3: Pattern Recognition

**User asks:**

```
"How do I usually play pocket jacks?"

LLM searches: search_past_decisions("pocket jacks")

Finds 12 past decisions with JJ:
- 8 times from late position → Raised 75% of the time
- 4 times from early position → Folded 50%, called 50%
- Win rate when raised: 62%
- Win rate when called: 45%

LLM Response:
"You've played pocket jacks 12 times. From late position, you're aggressive
(raising 75%) with a 62% win rate - good strategy! But from early position,
you're too passive. Consider raising more from early position to avoid tough
post-flop spots."
```

---

## Storage & Performance

### Pinecone Storage

**Per Decision Pair (Pre + Post):**
- Pre-decision: ~2 KB
- Post-decision: ~1 KB
- **Total: ~3 KB per decision**

**Typical Session:**
- 50 hands × 4 decisions per hand = 200 decisions
- 200 × 3 KB = **600 KB per session**

**Free Tier Capacity:**
- Pinecone free tier: 1 GB
- Can store ~166,000 decisions (~800 sessions)
- **More than enough for most players!**

### Search Performance

**Semantic Search:**
- Query time: 50-150ms (serverless Pinecone)
- Returns top-k most similar decisions
- Sorted by cosine similarity

**Embedding Model:**
- `all-MiniLM-L6-v2` (384 dimensions)
- Same model used for both storage and search
- Ensures accurate similarity matching

---

## Configuration

### Enable/Disable Decision Tracking

**In `main.py` or game initialization:**

```python
gui = PygameGUI(
    game=game,
    agent_manager=agent_manager,
    enable_hand_history=True,       # Save complete hands
    enable_decision_tracking=True   # NEW: Track each decision
)
```

**Set to `False` to disable:**
- No decisions will be saved to Pinecone
- `search_past_decisions` tool will return "not available"
- LLM won't have access to decision history

### Environment Variables

**Required:**

```bash
# .env file
PINECONE_API_KEY=your-pinecone-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
```

**Get API keys:**
- Pinecone: https://www.pinecone.io/ (free tier available)
- DeepSeek: https://platform.deepseek.com/

---

## Troubleshooting

### "Decision history not available"

**Cause:** Decision tracking not enabled or failed to initialize

**Fix:**
1. Check `.env` has `PINECONE_API_KEY`
2. Verify `enable_decision_tracking=True` in GUI init
3. Check console for error messages during startup

### "No similar past decisions found"

**Cause:** Not enough decisions saved yet, or query too specific

**Fix:**
1. Play more hands to build up decision history
2. Use broader queries (e.g., "pocket pair" instead of "pocket threes on button")
3. Check Pinecone dashboard to verify decisions are being saved

### Pre-decision saved but no post-decision

**Cause:** Action failed or was canceled

**Fix:**
- For raises, ensure you confirm (don't cancel)
- Check game logs for action execution errors

### Decisions not linking to hand outcomes

**Cause:** Hand outcome update failed

**Fix:**
- Check `_track_hand_end()` logs
- Verify `finalize_hand_decisions()` is being called
- Ensure `hand_id` matches between decisions and hand

---

## Best Practices

### 1. Build Decision History Gradually

- Play at least 50-100 hands before relying on decision history
- More decisions = better similarity matches
- System improves over time as you play

### 2. Use Descriptive Queries

**Good queries:**
- "pocket aces facing 3-bet from tight player"
- "top pair on draw-heavy board in position"
- "missed flush draw facing river bet"

**Poor queries:**
- "what do?" (too vague)
- "jacks" (too short)

### 3. Review Past Decisions Regularly

Ask the LLM:
- "Show my worst decisions from last session"
- "How often do I bluff?"
- "What's my win rate with suited connectors?"

### 4. Combine with Other Tools

LLM should use MULTIPLE tools together:
```
User: "Should I call?"

LLM uses:
1. get_game_state() → Current situation
2. calculate_pot_odds() → Mathematical analysis
3. search_past_decisions() → Your history
4. search_poker_knowledge() → General strategy

Final advice combines all 4 sources!
```

---

## Advanced Features (Future Enhancements)

### Planned Improvements

1. **Outcome Attribution**
   - Link post-decisions with actual outcomes
   - Show "You raised here and won $120"
   - Calculate ROI for different actions

2. **Decision Clustering**
   - Automatically group similar decisions
   - Identify recurring patterns
   - Suggest adjustments

3. **Comparative Analysis**
   - "You vs optimal strategy"
   - Highlight -EV decisions
   - Suggest alternative actions

4. **Export & Analysis**
   - Export decision history to CSV
   - Generate reports
   - Track improvement over time

---

## API Reference

### DecisionTracker Methods

```python
tracker = DecisionTracker(pinecone_store=None)

# Hand lifecycle
tracker.start_hand(hand_id: str)
tracker.finalize_hand_decisions(hand_id: str, outcome: str, profit: int)

# Decision saving
tracker.save_pre_decision(
    decision_id: str,
    game_state: Dict,
    your_cards: List[str],
    position: str,
    previous_actions: List[Dict] = None
) -> bool

tracker.save_post_decision(
    decision_id: str,
    action: ActionType,
    amount: int,
    chips_after: int,
    pot_after: int
) -> bool

# Searching
tracker.search_similar_decisions(
    query: str,
    decision_type: str = 'pre_decision',  # or 'post_decision'
    filters: Optional[Dict] = None,
    top_k: int = 5
) -> List[Dict]

# Helper methods
tracker.generate_decision_id() -> str
```

---

## Summary

The Decision-Action Tracking System provides:

✅ **Complete Decision Records**: Pre-state, action, outcome
✅ **Semantic Search**: Find similar past situations
✅ **LLM Integration**: AI advisor uses your history
✅ **Real-time Advice**: Learn from your own experience
✅ **Post-game Analysis**: Review and improve

**Key Insight**: Instead of just generic poker strategy, the LLM now tells you *what YOU did in similar spots* and *what worked for YOU*.

This creates a **personalized poker coach** that learns your playing style and helps you improve based on YOUR actual results!

---

## Next Steps

1. ✅ **Play poker** - Build up decision history
2. ✅ **Ask the LLM** - "What did I do with pocket jacks?"
3. ✅ **Review decisions** - "Show my worst folds"
4. ✅ **Track improvement** - Compare decisions over time
5. ✅ **Adjust strategy** - Learn from patterns in your play

Happy decision tracking! 🎰🃏
