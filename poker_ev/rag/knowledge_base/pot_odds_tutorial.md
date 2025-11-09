# Pot Odds Tutorial: Step-by-Step Guide

## What Are Pot Odds?

**Pot odds** are the ratio of the pot size to the cost of your call. They tell you how much you need to win to make a call profitable.

**Simple definition**: How much are you risking vs. how much you could win?

## The Basic Formula

```
Pot Odds = Cost to Call : Pot Size
```

Or as a percentage:

```
Pot Odds % = Cost to Call / (Pot + Cost to Call)
```

## Step-by-Step Method

### Step 1: Calculate the Pot Size

**Before** the current bet, how much is in the pot?

### Step 2: Determine Cost to Call

How much do you need to put in to stay in the hand?

### Step 3: Calculate Total Pot (If You Call)

```
Total Pot = Current Pot + Opponent's Bet + Your Call
```

### Step 4: Calculate Pot Odds Percentage

```
Pot Odds % = Your Call / Total Pot
```

### Step 5: Compare to Your Equity

- If **Equity > Pot Odds**: CALL (profitable)
- If **Equity < Pot Odds**: FOLD (unprofitable)
- If **Equity = Pot Odds**: BREAKEVEN (neutral)

## Worked Example 1: Simple Pot Odds

### The Situation
**Pot before bet**: $100
**Opponent bets**: $50
**Your hand**: Flush draw (9 outs, ~36% equity on flop)

### Step-by-Step Solution

**Step 1: Pot size before bet** = $100

**Step 2: Cost to call** = $50

**Step 3: Total pot if you call** = $100 + $50 + $50 = $200

**Step 4: Pot odds percentage**
```
Pot Odds = $50 / $200 = 0.25 = 25%
```

You need 25% equity to call profitably.

**Step 5: Compare equity to pot odds**
- Your equity: 36%
- Required equity (pot odds): 25%
- **Decision: CALL** (you have more equity than required)

### Understanding the Result
You're investing $50 to win $200, which is 1:4 odds (25%). Since you'll win this hand about 36% of the time, you're getting a good price.

**Long-term expectation**:
- Win 36% of the time: 0.36 × $200 = $72
- Cost: $50
- **Profit: +$22 per call** (in the long run)

## Worked Example 2: Bad Pot Odds

### The Situation
**Pot before bet**: $60
**Opponent bets**: $80
**Your hand**: Gutshot straight draw (4 outs, ~8% equity on turn)

### Step-by-Step Solution

**Step 1: Pot size before bet** = $60

**Step 2: Cost to call** = $80

**Step 3: Total pot if you call** = $60 + $80 + $80 = $220

**Step 4: Pot odds percentage**
```
Pot Odds = $80 / $220 = 0.36 = 36%
```

You need 36% equity to call profitably.

**Step 5: Compare equity to pot odds**
- Your equity: 8%
- Required equity (pot odds): 36%
- **Decision: FOLD** (you don't have enough equity)

### Understanding the Result
You're investing $80 to win $220, which is terrible odds for an 8% chance of winning. This is a clear fold.

**Long-term expectation**:
- Win 8% of the time: 0.08 × $220 = $17.60
- Cost: $80
- **Loss: -$62.40 per call** (in the long run)

## Worked Example 3: Multi-Street Decision

### The Situation (Flop)
**Pot before bet**: $50
**Opponent bets**: $25
**Your hand**: Open-ended straight draw (8 outs, ~32% equity)

### Step-by-Step Solution

**Step 1: Pot size before bet** = $50

**Step 2: Cost to call** = $25

**Step 3: Total pot if you call** = $50 + $25 + $25 = $100

**Step 4: Pot odds percentage**
```
Pot Odds = $25 / $100 = 0.25 = 25%
```

**Step 5: Compare equity to pot odds**
- Your equity: 32%
- Required equity: 25%
- **Decision: CALL** (clear call)

## Pot Odds as Ratios

### Common Ratio Conversions

| Ratio | Percentage | Meaning |
|-------|------------|---------|
| 1:1 | 50% | You need to win half the time |
| 2:1 | 33% | You need to win 1 in 3 times |
| 3:1 | 25% | You need to win 1 in 4 times |
| 4:1 | 20% | You need to win 1 in 5 times |
| 5:1 | 17% | You need to win 1 in 6 times |

### How to Convert Ratio to Percentage

```
Percentage = 1 / (Ratio + 1)
```

**Example**: 3:1 odds
```
Percentage = 1 / (3 + 1) = 1/4 = 25%
```

## Decision Trees

### Decision Tree 1: Flush Draw on Flop

```
Do you have a flush draw?
├─ YES → Count outs (usually 9)
│         ├─ Calculate equity: 9 × 4 = 36%
│         └─ Compare to pot odds
│             ├─ Pot odds < 36%? → CALL
│             └─ Pot odds > 36%? → FOLD (or consider implied odds)
└─ NO → Use different decision tree
```

### Decision Tree 2: General Drawing Hand

```
Step 1: Count your outs
         └─ Use systematic method

Step 2: Calculate equity
         ├─ Flop (2 cards to come): Outs × 4
         └─ Turn (1 card to come): Outs × 2

Step 3: Calculate pot odds
         └─ Call amount / (Pot + Call amount)

Step 4: Compare
         ├─ Equity > Pot odds? → CALL
         ├─ Equity < Pot odds? → FOLD (unless implied odds)
         └─ Equity ≈ Pot odds? → Consider position, implied odds
```

## Common Pot Odds Scenarios

### Scenario 1: Half-Pot Bet
**Opponent bets**: Half the pot
**Pot odds**: 2:1 (33%)
**Equity needed**: 33%

**Example**:
- Pot: $100
- Bet: $50
- You need: 33% equity to call

### Scenario 2: Pot-Sized Bet
**Opponent bets**: The pot
**Pot odds**: 2:1 (33%)
**Equity needed**: 33%

**Example**:
- Pot: $100
- Bet: $100
- You need: 33% equity to call

Wait, that doesn't seem right. Let me recalculate:
- Pot after bet: $100 + $100 = $200
- Cost to call: $100
- Total pot if you call: $200 + $100 = $300
- Pot odds: $100 / $300 = **33%**

Actually, it is 33%! Same as half-pot bet.

Actually no, let me recalculate more carefully:

**Half-pot bet**:
- Initial pot: $100
- Opponent bets: $50
- New pot: $150
- You call: $50
- Total pot: $200
- Pot odds: $50 / $200 = 25%

**Pot-sized bet**:
- Initial pot: $100
- Opponent bets: $100
- New pot: $200
- You call: $100
- Total pot: $300
- Pot odds: $100 / $300 = 33%

Let me redo this table:

### Scenario 1: Half-Pot Bet
**Opponent bets**: Half the pot
**Pot odds**: 3:1 (25%)
**Equity needed**: 25%

**Example**:
- Pot: $100
- Bet: $50
- Pot odds: $50 / $200 = 25%

### Scenario 2: Pot-Sized Bet
**Opponent bets**: The pot
**Pot odds**: 2:1 (33%)
**Equity needed**: 33%

**Example**:
- Pot: $100
- Bet: $100
- Pot odds: $100 / $300 = 33%

### Scenario 3: Overbet (1.5x Pot)
**Opponent bets**: 1.5× the pot
**Pot odds**: ~40%
**Equity needed**: 40%

**Example**:
- Pot: $100
- Bet: $150
- Pot odds: $150 / $400 = 37.5%

### Scenario 4: Small Bet (Quarter Pot)
**Opponent bets**: Quarter the pot
**Pot odds**: 5:1 (17%)
**Equity needed**: 17%

**Example**:
- Pot: $100
- Bet: $25
- Pot odds: $25 / $150 = 16.7%

## Practice Problems

### Problem 1: Basic Calculation
**Pot**: $80
**Opponent bets**: $40
**Your call**: $40

**What are your pot odds?**

<details>
<summary>Answer</summary>

**Step 1**: Pot before bet = $80
**Step 2**: Cost to call = $40
**Step 3**: Total pot = $80 + $40 + $40 = $160
**Step 4**: Pot odds = $40 / $160 = **25%**

You need 25% equity to call profitably.
</details>

### Problem 2: Call or Fold?
**Pot**: $120
**Opponent bets**: $60
**Your hand**: Flush draw (9 outs on flop)

**Should you call?**

<details>
<summary>Answer</summary>

**Pot odds**: $60 / ($120 + $60 + $60) = $60 / $240 = 25%

**Your equity**: 9 outs × 4 = 36%

**Decision**: **CALL** (36% equity > 25% required)
</details>

### Problem 3: Overbet Scenario
**Pot**: $50
**Opponent bets**: $100
**Your hand**: Open-ended straight draw (8 outs on turn)

**Should you call?**

<details>
<summary>Answer</summary>

**Pot odds**: $100 / ($50 + $100 + $100) = $100 / $250 = 40%

**Your equity**: 8 outs × 2 = 16%

**Decision**: **FOLD** (16% equity < 40% required)

This is a huge overbet and you don't have nearly enough equity.
</details>

### Problem 4: All-In Decision
**Pot**: $200
**Opponent goes all-in**: $150
**Your hand**: A♠K♠ vs opponent's likely pocket pair (you have ~47% equity)

**Should you call?**

<details>
<summary>Answer</summary>

**Pot odds**: $150 / ($200 + $150 + $150) = $150 / $500 = 30%

**Your equity**: ~47%

**Decision**: **CALL** (47% equity > 30% required)

This is a profitable call even though you're slightly behind in equity.
</details>

### Problem 5: Multiple Callers
**Pot**: $60
**Player 1 bets**: $30
**Player 2 calls**: $30
**Your hand**: Flush draw (9 outs on flop)

**What are your pot odds now?**

<details>
<summary>Answer</summary>

**Step 1**: Pot before action = $60
**Step 2**: After Player 1 bets = $60 + $30 = $90
**Step 3**: After Player 2 calls = $90 + $30 = $120
**Step 4**: Your cost to call = $30
**Step 5**: Total pot if you call = $120 + $30 = $150

**Pot odds**: $30 / $150 = **20%**

**Your equity**: 9 × 4 = 36%

**Decision**: **CALL** (great pot odds with multiple players)

Note: With multiple players, you often get better pot odds!
</details>

## Common Mistakes

### Mistake 1: Forgetting to Include Your Call
❌ **Wrong**: Pot odds = Cost / Current Pot
✅ **Right**: Pot odds = Cost / (Current Pot + Cost)

### Mistake 2: Using Wrong Equity Calculation
❌ **Wrong**: Using flop equity (outs × 4) when on the turn
✅ **Right**: Use turn equity (outs × 2) when one card to come

### Mistake 3: Only Considering Current Street
❌ **Wrong**: Ignoring future betting rounds
✅ **Right**: Consider implied odds for future value

### Mistake 4: Pot Odds with Multiple Bets
❌ **Wrong**: Calculating pot odds before all bets are in
✅ **Right**: Wait for all action before you to complete

## Quick Reference

**Basic Pot Odds Calculation**:
```
1. Pot before bet
2. Add opponent's bet(s)
3. Add your call
4. Your call / Total pot = Pot odds %
5. Compare to equity
```

**Quick equity estimates**:
- Flush draw: ~36% (flop) or ~18% (turn)
- Open-ended straight: ~32% (flop) or ~16% (turn)
- Gutshot: ~16% (flop) or ~8% (turn)

## Summary

1. **Pot odds** = Cost to call / (Pot + Cost)
2. **Call when equity > pot odds**
3. **Consider implied odds** for future value
4. **Practice** until calculations become automatic

Mastering pot odds is essential for profitable poker. Once you're comfortable with these calculations, you're ready to learn about implied odds and expected value!
