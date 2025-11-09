# Common Probability Mistakes: Error Correction Guide

## Introduction

Even experienced poker players make probability mistakes. This guide identifies common errors and explains the correct approach.

## Category 1: Counting Outs

### Mistake 1.1: Double-Counting Outs

**Scenario**: Flush draw + pair draw

**Your hand**: A♠9♠
**Board**: K♠7♠2♦

❌ **Wrong thinking**:
- Flush outs: 9 spades
- Aces to pair: 3 aces
- Nines to pair: 3 nines
- Total: 9 + 3 + 3 = 15 outs

✅ **Correct thinking**:
- Flush outs: 9 spades
- Non-spade aces: 2 aces (A♥, A♦)
- Non-spade nines: 2 nines (9♥, 9♦)
- **Total: 9 + 2 + 2 = 13 outs**

**Why**: The A♠ and 9♠ are already counted in the flush outs!

### Mistake 1.2: Counting Tainted Outs

**Scenario**: Straight draw on paired board

**Your hand**: J♣T♣
**Board**: 9♠8♠8♦

❌ **Wrong thinking**:
- Straight outs: 4 queens + 4 sevens = 8 outs
- Equity: 8 × 4 = 32%

✅ **Correct thinking**:
- If opponent has an 8, queens and sevens give them a full house
- If opponent has an overpair (AA, KK, QQ), a queen might not be good
- **Discount 1-2 outs: ~6-7 clean outs**

**Why**: Some outs improve your hand but give opponent a better hand.

### Mistake 1.3: Not Counting All Outs

**Scenario**: Flush draw + overcards

**Your hand**: A♥K♥
**Board**: Q♥7♥3♠

❌ **Wrong thinking**:
- Flush outs only: 9 hearts
- Equity: 36%

✅ **Correct thinking**:
- Flush outs: 9 hearts
- Non-heart aces: 3 aces (minus A♥) = 2
- Non-heart kings: 3 kings (minus K♥) = 2
- **Total: 9 + 2 + 2 = 13 outs** (assuming overcards are good)

**Why**: Pairing your ace or king might win the pot too!

### Mistake 1.4: Overvaluing Gutshot + Overcards

**Scenario**: Gutshot + two overcards

**Your hand**: A♠K♦
**Board**: Q♣J♠5♥

❌ **Wrong thinking**:
- Gutshot (T): 4 outs
- Aces: 3 outs
- Kings: 3 outs
- Total: 10 outs
- Equity: 40%

✅ **Correct thinking**:
- Against a hand like QJ (two pair), an ace or king doesn't help
- Against J-9 (straight draw), tens and aces are bad for you
- **Realistic outs: 4 (gutshot only) if opponent is strong**

**Why**: Overcards aren't outs if opponent already has two pair or better.

## Category 2: Pot Odds Calculation

### Mistake 2.1: Forgetting to Include Your Call

❌ **Wrong calculation**:
- Pot: $100
- Bet: $50
- Pot odds: $50 / $100 = 50%

✅ **Correct calculation**:
- Pot after opponent bets: $150
- Your call: $50
- Total pot if you call: $200
- **Pot odds: $50 / $200 = 25%**

**Why**: You need to include your call in the total pot!

### Mistake 2.2: Using Wrong Equity for Street

❌ **Wrong thinking**:
- On turn with flush draw
- Equity: 9 × 4 = 36%

✅ **Correct thinking**:
- On turn (one card to come)
- **Equity: 9 × 2 = 18%**

**Why**: Rule of 4 is for the flop (two cards to come), not the turn!

### Mistake 2.3: Confusing Odds Formats

❌ **Wrong thinking**:
- Pot odds: 3:1
- Need: 3% equity to call

✅ **Correct thinking**:
- Pot odds: 3:1
- **Need: 1/(3+1) = 1/4 = 25% equity to call**

**Why**: 3:1 means you win 1 out of 4 times, which is 25%, not 3%!

## Category 3: Expected Value

### Mistake 3.1: Forgetting Cost in EV Calculation

❌ **Wrong calculation**:
- Win 30% of the time: Win $100
- EV = 0.30 × $100 = $30

✅ **Correct calculation**:
- Win 30% of the time: Win $100
- Lose 70% of the time: Lose $40
- **EV = (0.30 × $100) - (0.70 × $40) = $30 - $28 = +$2**

**Why**: EV must account for both wins AND losses!

### Mistake 3.2: Not Considering All Outcomes

**Scenario**: Bluffing decision

❌ **Wrong thinking**:
- If opponent folds (50%): Win $100
- EV = 0.50 × $100 = $50

✅ **Correct thinking**:
- If opponent folds (50%): Win $100
- If opponent calls (50%): Lose $75 (your bluff)
- **EV = (0.50 × $100) - (0.50 × $75) = $50 - $37.50 = +$12.50**

**Why**: Must include what happens when opponent calls!

### Mistake 3.3: Ignoring Fold Equity

**Scenario**: Semi-bluff with draw

❌ **Wrong calculation**:
- Equity if called: 30%
- Not enough to call pot odds (need 40%)
- Conclusion: Fold

✅ **Correct thinking**:
- Equity if called: 30%
- Opponent folds: 25%
- Raising has positive EV from fold equity
- **Conclusion: Raise, don't call or fold**

**Why**: Aggression adds value through fold equity!

## Category 4: Implied Odds

### Mistake 4.1: Overestimating Future Value

❌ **Wrong thinking**:
- Gutshot (8% equity)
- Bad pot odds (need 40%)
- "But I'll win $500 more if I hit!"
- Call

✅ **Correct thinking**:
- Will opponent really pay $500 when straight comes?
- Opponent's stack: $150
- Board texture: Straight will be obvious
- **Realistic future winnings: $30-50**
- **Conclusion: Fold, not enough implied odds**

**Why**: Be realistic about how much you'll actually win!

### Mistake 4.2: Calling with Reverse Implied Odds

**Scenario**: Small flush draw

**Your hand**: 6♥5♥
**Board**: K♥9♥3♠

❌ **Wrong thinking**:
- Flush draw: 9 outs
- Great implied odds (opponent has top pair)
- Call

✅ **Correct thinking**:
- If a heart comes, opponent with A♥ or Q♥ beats you
- You might make flush and still lose big pot
- **Reverse implied odds are significant**
- Call is risky

**Why**: Small flush draws can be traps when stacks are deep!

### Mistake 4.3: Ignoring Stack Sizes

❌ **Wrong thinking**:
- Set mining with 7-7
- Pot: $15, call: $10
- Good implied odds because opponent has a strong hand

✅ **Correct thinking**:
- Opponent's stack: $50
- Not enough behind to make up for 12% chance of hitting
- **SPR too low for set mining**

**Why**: Need deep stacks (15:1 or more) for set mining!

## Category 5: Hand Reading

### Mistake 5.1: Assuming Outs Are Good

**Scenario**: Drawing dead

**Your hand**: A♠K♣
**Board**: Q♠J♠T♦9♠
**Opponent**: Has J♥8♥ (straight)

❌ **Wrong thinking**:
- I have 8 outs (4 aces + 4 kings)
- Equity: 16%

✅ **Correct thinking**:
- Any ace or king gives opponent a higher straight
- **You're drawing dead to a straight**
- You actually need a spade (flush) to win
- Real outs: Only A♠

**Why**: Must consider opponent's likely holdings!

### Mistake 5.2: Not Adjusting for Board Texture

**Scenario**: Overcards on scary board

**Your hand**: A♥K♦
**Board**: 9♠8♠7♠

❌ **Wrong thinking**:
- Two overcards: 6 outs
- Equity: 24%

✅ **Correct thinking**:
- Flush already on board
- Opponent likely has at least one spade
- Pairing ace or king doesn't help
- **Realistic outs: 0-2**

**Why**: Board texture drastically affects your outs!

## Category 6: Multi-Way Pots

### Mistake 6.1: Using Heads-Up Equity

❌ **Wrong thinking**:
- Flush draw in 3-way pot
- Equity: 36%
- Compare to pot odds normally

✅ **Correct thinking**:
- Against two opponents, flush draw has ~27% equity
- Need to adjust expectations downward
- **Your piece of the pie is smaller**

**Why**: Equity is split among more players!

### Mistake 6.2: Not Getting Right Price Multi-Way

❌ **Wrong thinking**:
- Pot: $150 (3 players already in)
- Bet to call: $50
- Pot odds: 25%
- My flush draw: 36%
- Call!

✅ **Correct thinking**:
- With 3 players, flush draw is ~27% equity
- Pot odds: 25%
- **Barely profitable, but position matters**
- If out of position, fold

**Why**: Multi-way reduces your equity!

## Category 7: Mental Errors

### Mistake 7.1: Results-Oriented Thinking

❌ **Wrong thinking**:
- "I called with 25% equity against 40% pot odds requirement"
- "I hit my card and won"
- "That was a good call!"

✅ **Correct thinking**:
- Call was -EV even though I won this time
- Over 100 times, I'd lose money
- **Outcome doesn't change whether decision was correct**

**Why**: Focus on process, not results!

### Mistake 7.2: Gambler's Fallacy

❌ **Wrong thinking**:
- "I've missed my flush draw 5 times in a row"
- "I'm due to hit it this time"
- Call with bad odds

✅ **Correct thinking**:
- Each draw is independent
- Past results don't affect future probabilities
- **Still only 18% to hit on this turn**

**Why**: Cards have no memory!

### Mistake 7.3: Recency Bias

❌ **Wrong thinking**:
- "Last session I called here and got crushed"
- "I should fold this time even with good odds"

✅ **Correct thinking**:
- Equity: 40%
- Pot odds required: 30%
- **This is a profitable call regardless of last session**

**Why**: Each decision is independent!

## Category 8: Advanced Mistakes

### Mistake 8.1: Assuming Static Ranges

❌ **Wrong thinking**:
- Opponent has same range on every street
- Calculate equity vs their range once

✅ **Correct thinking**:
- Ranges narrow each street based on actions
- Opponent's flop range ≠ turn range
- **Recalculate equity as range updates**

**Why**: Hand reading is dynamic!

### Mistake 8.2: Confusing EV and Variance

❌ **Wrong thinking**:
- "This play has high EV"
- "I should make this play all the time even though it's risky"

✅ **Correct thinking**:
- Play has high EV but also high variance
- Consider bankroll management
- **Positive EV + high variance = need proper bankroll**

**Why**: Going broke on +EV plays is still going broke!

## Quick Reference: Common Mistakes Checklist

Before making a decision, ask yourself:

- [ ] Did I count all my outs?
- [ ] Did I double-count any outs?
- [ ] Are my outs "clean" or "tainted"?
- [ ] Did I use Rule of 4 (flop) or Rule of 2 (turn) correctly?
- [ ] Did I include my call in pot odds calculation?
- [ ] Did I account for both wins and losses in EV?
- [ ] Am I being realistic about implied odds?
- [ ] Am I considering reverse implied odds?
- [ ] Is my hand strong enough against opponent's likely range?
- [ ] Am I thinking about process or just results?

## Summary

1. **Double-counting outs** is the most common mistake
2. **Pot odds** must include your call in the total pot
3. **EV calculations** require subtracting your investment
4. **Implied odds** are often overestimated
5. **Board texture** and hand reading affect your true outs
6. **Results-oriented thinking** leads to bad long-term decisions
7. **Independent events** means past results don't affect future probabilities

Avoiding these common mistakes will dramatically improve your win rate. Review this guide regularly to reinforce correct thinking!
