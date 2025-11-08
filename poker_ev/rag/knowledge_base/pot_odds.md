# Pot Odds and Expected Value

## What Are Pot Odds?

**Pot odds** are the ratio between the current size of the pot and the cost of a contemplated call. They help determine whether calling a bet is mathematically profitable.

### Formula
```
Pot Odds = Amount to Call / (Current Pot + Amount to Call)
```

### Example
- **Pot**: $100
- **Opponent bets**: $50
- **New pot**: $150
- **You must call**: $50
- **Pot odds**: $50 / ($150 + $50) = $50 / $200 = **25%**

This means you need to win 25% of the time to break even.

## Calculating Equity

**Equity** is your percentage chance of winning the hand.

### Counting Outs

An "out" is a card that will improve your hand to likely the best hand.

#### Common Draw Outs

| Draw Type | Example | Outs | Turn Equity | Turn + River Equity |
|-----------|---------|------|-------------|---------------------|
| Inside Straight | You: 9-8, Board: K-7-5 | 4 | ~9% | ~17% |
| One Overcard | You: A-7, Board: K-8-2 | 3 | ~6% | ~13% |
| Two Overcards | You: A-K, Board: 9-7-2 | 6 | ~13% | ~24% |
| Open-Ended Straight | You: 10-9, Board: 8-7-2 | 8 | ~17% | ~31% |
| Flush Draw | You: A♠ K♠, Board: 9♠ 4♠ 2♥ | 9 | ~19% | ~35% |
| Flush + Straight | You: 10♠ 9♠, Board: 8♠ 7♠ 2♥ | 15 | ~32% | ~54% |

### Rule of 2 and 4

Quick mental math for equity:
- **On the flop** (two cards to come): Outs × 4 = Equity %
- **On the turn** (one card to come): Outs × 2 = Equity %

**Example**: Flush draw (9 outs) on flop
- Equity ≈ 9 × 4 = 36% (actual: ~35%)

## Pot Odds vs. Equity Decision

### The Break-Even Rule

**Call if**: Your equity > Pot odds required
**Fold if**: Your equity < Pot odds required

### Example 1: Flush Draw
- **Situation**: You have flush draw (35% equity)
- **Pot**: $100
- **Bet**: $50
- **Pot odds**: 25% (you need to win 25% to break even)
- **Decision**: CALL (35% > 25%)

### Example 2: Inside Straight Draw
- **Situation**: You have gutshot (17% equity)
- **Pot**: $50
- **Bet**: $30
- **Pot odds**: 37.5% (you need to win 37.5% to break even)
- **Decision**: FOLD (17% < 37.5%)

## Implied Odds

**Implied odds** consider future betting rounds. If you hit your draw, how much more can you win?

### When to Consider Implied Odds
1. **Deep stacks**: More chips to win on later streets
2. **Hidden hands**: Your hand is disguised (e.g., small pocket pairs for sets)
3. **Passive opponents**: Likely to pay you off when you hit

### Example
- **Current pot**: $50
- **Bet to call**: $20
- **Your outs**: 8 (open-ended straight)
- **Direct pot odds**: 22% required (you have ~31%)
- **If you hit**: Opponent has $200 behind and might bet $100 more
- **Implied pot**: $50 + $100 = $150
- **Implied odds**: Much better than direct odds

### Reverse Implied Odds

Sometimes even when you hit, you can lose more money:
- **Example**: You have weak flush draw (7♣ 2♣), board is K♣ 9♣ 3♠
- **Risk**: If a club comes, opponent might have higher flush
- **Decision**: Fold even with correct direct pot odds

## Expected Value (EV)

**EV** = (Probability of Winning × Amount Won) - (Probability of Losing × Amount Lost)

### Positive EV vs. Negative EV

- **+EV**: Profitable play over the long run
- **-EV**: Losing play over the long run

### Example Calculation

**Situation**:
- Pot: $100
- Opponent bets: $50 (pot now $150)
- You have flush draw: 35% equity
- Call: $50

**EV Calculation**:
```
EV = (0.35 × $150) - (0.65 × $50)
EV = $52.50 - $32.50
EV = +$20
```

**Decision**: CALL (positive EV)

## Common Pot Odds Scenarios

### Scenario 1: Flop Call with Draw
- **Your hand**: 10♠ 9♠
- **Board**: 8♠ 7♥ 2♣
- **Your equity**: 31% (8 outs × 4)
- **Pot**: $80
- **Bet**: $40
- **Pot odds**: 25% required
- **Decision**: CALL ✓

### Scenario 2: Turn Call with Draw
- **Your hand**: A♦ K♦
- **Board**: Q♦ 7♦ 3♠ 2♥
- **Your equity**: 18% (9 outs × 2)
- **Pot**: $120
- **Bet**: $80
- **Pot odds**: 40% required
- **Decision**: FOLD ✗ (unless strong implied odds)

### Scenario 3: Set Mining
- **Your hand**: 4♣ 4♠
- **Opponent raises**: $10
- **Pot**: $12
- **Set odds**: ~12% (1 in 8)
- **Pot odds**: 45% required
- **Direct odds**: BAD
- **Implied odds**: If you flop a set, opponent might pay you $100+
- **Decision**: CALL if stacks are deep enough (10:1 rule)

## The 10:1 Rule for Set Mining

To profitably call with small pocket pairs hoping to flop a set:
- **Opponent's stack should be 10x the call amount**

**Example**:
- **Call**: $10
- **Opponent's stack**: $100+
- **Reasoning**: You'll flop a set 12% of the time, but when you do, you can win a big pot

## Multi-Way Pot Odds

When multiple players are in the pot:
- **Your equity often increases** (more ways to win)
- **But implied odds decrease** (harder to get paid off)
- **Be more cautious** with marginal draws

### Example
- **3 players in pot**
- **Pot**: $150
- **Bet**: $50
- **Pot odds**: 20% required
- **Your flush draw**: 35% to win
- **Decision**: Still CALL, but be aware someone else might also have a draw

## Common Mistakes

### Mistake 1: Chasing Without Odds
- **Problem**: Calling with 20% equity when pot odds require 40%
- **Cost**: Hemorrhaging chips over time

### Mistake 2: Ignoring Reverse Implied Odds
- **Problem**: Chasing weak draws (e.g., bottom pair draw)
- **Cost**: Making hand but losing to better hand

### Mistake 3: Not Considering Implied Odds
- **Problem**: Folding draws with poor direct odds but huge implied odds
- **Cost**: Missing profitable situations

### Mistake 4: Overestimating Outs
- **Problem**: Counting outs that don't make the winning hand
- **Example**: Drawing to a straight when board is two-suited (might make flush)

## Advanced Concepts

### Fold Equity
- **Definition**: The value gained from opponent folding
- **Application**: Bluffing and semi-bluffing with draws

### Pot Odds in 3-Bet Pots
- **Larger pots**: Better pot odds for calling
- **More opponents**: Reduced fold equity

### Blockers and Combinatorics
- **Blockers**: Cards in your hand reduce opponent's possible holdings
- **Example**: You have A♠, fewer combinations of A-A for opponent
