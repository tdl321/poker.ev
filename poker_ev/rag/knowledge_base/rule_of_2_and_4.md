# The Rule of 2 and 4: Quick Equity Calculation

## What Is the Rule of 2 and 4?

The **Rule of 2 and 4** is a mental math shortcut for quickly estimating your equity (win probability) based on your outs.

### The Rule

**On the flop** (with 2 cards to come):
```
Equity % ≈ Outs × 4
```

**On the turn** (with 1 card to come):
```
Equity % ≈ Outs × 2
```

### Why It Works

This rule is based on the probability of hitting your outs with the remaining cards in the deck.

## The Math Behind It

### Turn to River (1 Card to Come)

**Total unseen cards**: 46 (52 - 2 hole cards - 4 board cards = 46)

**If you have X outs**:
```
Exact equity = X / 46
```

**Convert to percentage**:
```
Equity % = (X / 46) × 100
         = X × 2.17
         ≈ X × 2
```

**Example**: 9 outs on the turn
- Exact: (9 / 46) × 100 = 19.6%
- Rule of 2: 9 × 2 = 18%
- **Error: -1.6%** (very close!)

### Flop to River (2 Cards to Come)

This is more complex because you see two cards, but the approximation still works well.

**Simplified calculation**:
```
Equity % ≈ (X / 47) × 100 + (X / 46) × 100
         ≈ X × 4.26
         ≈ X × 4
```

**Example**: 9 outs on the flop
- Exact: 35%
- Rule of 4: 9 × 4 = 36%
- **Error: +1%** (excellent!)

## Accuracy of the Rule

### When Is It Most Accurate?

The Rule of 2 and 4 is most accurate for **4-12 outs**.

| Outs | Exact (Flop) | Rule of 4 | Error |
|------|--------------|-----------|-------|
| 4    | 16.5%        | 16%       | -0.5% |
| 6    | 24.1%        | 24%       | -0.1% |
| 8    | 31.5%        | 32%       | +0.5% |
| 9    | 35.0%        | 36%       | +1.0% |
| 12   | 45.0%        | 48%       | +3.0% |
| 15   | 54.1%        | 60%       | +5.9% |

### When Does It Break Down?

**For 15+ outs** (monster draws), the rule overestimates equity significantly.

**Better rule for 15+ outs**:
```
Equity % ≈ (Outs × 4) - (Outs - 8)
```

**Example**: 15 outs
- Rule of 4: 15 × 4 = 60%
- Adjusted: (15 × 4) - (15 - 8) = 60 - 7 = 53%
- Exact: 54.1%
- **Much better!**

## Common Situations

### Flush Draw (9 Outs)

**On the flop**:
- Rule of 4: 9 × 4 = **36%**
- Exact: 35%

**On the turn**:
- Rule of 2: 9 × 2 = **18%**
- Exact: 19.6%

### Open-Ended Straight Draw (8 Outs)

**On the flop**:
- Rule of 4: 8 × 4 = **32%**
- Exact: 31.5%

**On the turn**:
- Rule of 2: 8 × 2 = **16%**
- Exact: 17.4%

### Gutshot (4 Outs)

**On the flop**:
- Rule of 4: 4 × 4 = **16%**
- Exact: 16.5%

**On the turn**:
- Rule of 2: 4 × 2 = **8%**
- Exact: 8.7%

### Two Overcards (6 Outs)

**On the flop**:
- Rule of 4: 6 × 4 = **24%**
- Exact: 24.1%

**On the turn**:
- Rule of 2: 6 × 2 = **12%**
- Exact: 13.0%

### Combo Draw: Flush + Straight (15 Outs)

**On the flop**:
- Rule of 4: 15 × 4 = 60%
- Adjusted: 60 - (15 - 8) = **53%**
- Exact: 54.1%

**On the turn**:
- Rule of 2: 15 × 2 = 30%
- Adjusted: Not needed for turn
- Exact: 32.6%

## Using the Rule at the Table

### Step-by-Step Process

**1. Count your outs**
- Flush draw: 9
- OESD: 8
- Gutshot: 4
- Overcards: 6

**2. Determine the street**
- Flop: Use × 4
- Turn: Use × 2

**3. Multiply**
- Quick mental math

**4. Compare to pot odds**
- Call if equity > pot odds

### Example: Real-Time Decision

**Situation**:
- You have: A♥9♥
- Board: K♥7♥2♣
- Pot: $100
- Opponent bets: $50

**Step 1: Count outs**
- Flush draw: 9 outs

**Step 2: Street**
- Flop (2 cards to come): Use × 4

**Step 3: Calculate equity**
- 9 × 4 = 36%

**Step 4: Calculate pot odds**
- Cost: $50
- Total pot: $100 + $50 + $50 = $200
- Pot odds: $50/$200 = 25%

**Step 5: Compare**
- Equity (36%) > Pot odds (25%)
- **CALL!**

**Time taken**: Less than 5 seconds!

## Practice Problems

### Problem 1: Flush Draw on Turn
**Your outs**: 9
**Street**: Turn

**What's your equity?**

<details>
<summary>Answer</summary>

9 × 2 = **18%**

(Exact: 19.6%)
</details>

### Problem 2: OESD on Flop
**Your outs**: 8
**Street**: Flop

**What's your equity?**

<details>
<summary>Answer</summary>

8 × 4 = **32%**

(Exact: 31.5%)
</details>

### Problem 3: Monster Draw
**Your outs**: 15 (flush draw + straight draw)
**Street**: Flop

**What's your equity using the standard rule? What's a better estimate?**

<details>
<summary>Answer</summary>

**Standard rule**: 15 × 4 = 60%

**Better estimate**: 60 - (15 - 8) = 60 - 7 = **53%**

(Exact: 54.1%)

The adjusted formula is more accurate for big draws.
</details>

### Problem 4: Gutshot on Turn
**Your outs**: 4
**Street**: Turn

**What's your equity?**

<details>
<summary>Answer</summary>

4 × 2 = **8%**

(Exact: 8.7%)
</details>

### Problem 5: Two Overcards on Flop
**Your hand**: A♠K♦
**Board**: 9♥7♣3♠
**Your outs**: 6 (3 aces + 3 kings)

**What's your equity?**

<details>
<summary>Answer</summary>

6 × 4 = **24%**

(Exact: 24.1%)

This assumes pairing either card will win, which may not always be true!
</details>

## Advanced: When the Rule Breaks Down

### Very Few Outs (1-3)

**1 out**:
- Rule of 4: 4%
- Exact (flop): 4.3%
- Error: -0.3%

**2 outs**:
- Rule of 4: 8%
- Exact (flop): 8.4%
- Error: -0.4%

**Verdict**: Rule is still pretty good, but slightly underestimates.

### Many Outs (15+)

**15 outs**:
- Rule of 4: 60%
- Exact (flop): 54.1%
- Error: +5.9% (overestimate)

**18 outs**:
- Rule of 4: 72%
- Exact (flop): 62.4%
- Error: +9.6% (large overestimate)

**Verdict**: Use the adjusted formula for 15+ outs.

## The Adjusted Formula (For 15+ Outs)

```
Equity % ≈ (Outs × 4) - (Outs - 8)
```

**Simplify**:
```
Equity % ≈ (Outs × 3) + 8
```

**Example with 15 outs**:
- (15 × 3) + 8 = 45 + 8 = 53%
- Exact: 54.1%
- Error: -1.1% (much better!)

**Example with 18 outs**:
- (18 × 3) + 8 = 54 + 8 = 62%
- Exact: 62.4%
- Error: -0.4% (excellent!)

## Why × 4 Works (Detailed Proof)

### Two Cards to Come

**Probability of NOT hitting** on turn:
```
P(miss turn) = (46 - Outs) / 46
```

**Probability of NOT hitting** on river (given missed turn):
```
P(miss river | miss turn) = (45 - Outs) / 45
```

**Probability of missing BOTH**:
```
P(miss both) = [(46 - Outs) / 46] × [(45 - Outs) / 45]
```

**Probability of hitting at least once**:
```
P(hit) = 1 - P(miss both)
```

**Example with 9 outs**:
```
P(miss both) = (37/46) × (36/45)
             = 0.8043 × 0.8000
             = 0.6435

P(hit) = 1 - 0.6435 = 0.3565 = 35.65%
```

**Rule of 4**: 9 × 4 = 36%

**Error**: +0.35% (incredibly close!)

### Why × 2 Works (Turn to River)

**Probability of hitting**:
```
P(hit) = Outs / 46
```

**Convert to percentage**:
```
P(hit) % = (Outs / 46) × 100
         = Outs × 2.174
         ≈ Outs × 2
```

**Example with 9 outs**:
```
P(hit) = 9 / 46 = 0.1957 = 19.57%
```

**Rule of 2**: 9 × 2 = 18%

**Error**: -1.57% (very close!)

## Quick Reference Card

**Standard Draws (Flop)**:
- 4 outs (gutshot): 16%
- 6 outs (2 overcards): 24%
- 8 outs (OESD): 32%
- 9 outs (flush): 36%
- 12 outs (flush + pair): 48%
- 15 outs (flush + OESD): 53% (use adjusted)

**Standard Draws (Turn)**:
- 4 outs (gutshot): 8%
- 6 outs (2 overcards): 12%
- 8 outs (OESD): 16%
- 9 outs (flush): 18%
- 12 outs (flush + pair): 24%
- 15 outs (flush + OESD): 30%

## Summary

1. **Rule of 2 and 4** is incredibly accurate for 4-12 outs
2. **Flop**: Multiply outs by 4
3. **Turn**: Multiply outs by 2
4. **15+ outs**: Use adjusted formula (Outs × 3) + 8
5. **Practice** until it becomes automatic

This rule allows you to make instant equity calculations at the table without complex math. Master it and you'll make better decisions faster!
