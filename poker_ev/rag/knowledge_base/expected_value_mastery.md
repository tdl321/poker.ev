# Expected Value Mastery: Making Profitable Decisions

## What Is Expected Value (EV)?

**Expected Value (EV)** is the average amount you expect to win or lose from a decision if you made it many times.

**Simple definition**: How much money does this decision make (or lose) in the long run?

## The "100 Trials" Framework

The easiest way to understand EV is to imagine making the same decision 100 times.

### Example: Coin Flip Bet

**Bet**: $10 on heads
**Win**: $15 if heads (50% chance)
**Lose**: $10 if tails (50% chance)

**Over 100 flips**:
- Win 50 times: 50 × $15 = $750
- Lose 50 times: 50 × $10 = $500
- **Net profit**: $750 - $500 = $250

**Per flip**: $250 / 100 = **+$2.50 EV**

**Interpretation**: Every time you make this bet, you make $2.50 on average.

## The EV Formula

```
EV = (Probability of Win × Amount Won) - (Probability of Loss × Amount Lost)
```

Or more generally:

```
EV = Σ (Probability of Outcome × Value of Outcome)
```

## Basic EV Calculations

### Example 1: Simple Call Decision

**Situation**:
- Pot: $100
- Opponent bets: $50
- You have: Flush draw (9 outs = 18% on turn)

**If you call**:
- Win 18% of the time: Win $150 (pot + opponent's bet)
- Lose 82% of the time: Lose $50 (your call)

**EV Calculation**:
```
EV = (0.18 × $150) - (0.82 × $50)
   = $27 - $41
   = -$14
```

**Decision**: **FOLD** (negative EV)

**Interpretation**: Every time you make this call, you lose $14 on average.

### Example 2: Profitable Call

**Situation**:
- Pot: $100
- Opponent bets: $25
- You have: Flush draw (9 outs = 36% on flop)

**If you call**:
- Win 36% of the time: Win $125
- Lose 64% of the time: Lose $25

**EV Calculation**:
```
EV = (0.36 × $125) - (0.64 × $25)
   = $45 - $16
   = +$29
```

**Decision**: **CALL** (positive EV)

**Interpretation**: Every time you make this call, you make $29 on average.

### Example 3: All-In Decision

**Situation**:
- Pot: $200
- Opponent goes all-in: $100
- You have: A♠K♠ vs likely pocket pair (47% equity)

**If you call**:
- Win 47% of the time: Win $300
- Lose 53% of the time: Lose $100

**EV Calculation**:
```
EV = (0.47 × $300) - (0.53 × $100)
   = $141 - $53
   = +$88
```

**Decision**: **CALL** (very positive EV!)

**Interpretation**: Even though you're slightly behind, the pot odds make this a hugely profitable call worth $88 on average.

## The "100 Trials" Method

### Step-by-Step Process

**1. Imagine making this decision 100 times**

**2. Calculate how many times you win**
```
Wins = Equity × 100
```

**3. Calculate how many times you lose**
```
Losses = (1 - Equity) × 100
```

**4. Calculate total winnings**
```
Total Wins = Wins × Pot (after call)
```

**5. Calculate total losses**
```
Total Losses = Losses × Your Call Amount
```

**6. Calculate net profit**
```
Net Profit = Total Wins - Total Losses
```

**7. Divide by 100 to get EV per decision**
```
EV = Net Profit / 100
```

### Example: 100 Trials Method

**Situation**:
- Pot: $80
- Bet: $40
- Your equity: 30%

**Over 100 trials**:
- Win: 30 times
- Lose: 70 times

**Winnings**:
- 30 wins × $120 pot = $3,600

**Losses**:
- 70 losses × $40 call = $2,800

**Net**:
- $3,600 - $2,800 = $800

**EV per decision**:
- $800 / 100 = **+$8 EV**

This is a profitable call worth $8 each time!

## EV vs Pot Odds

### The Connection

**Pot Odds** tell you the minimum equity needed to break even.

**EV** tells you exactly how much you make or lose.

### Relationship

- **EV > 0**: Call (profitable)
- **EV = 0**: Indifferent (break even)
- **EV < 0**: Fold (unprofitable)

### Example: Breakeven Point

**Pot**: $100
**Bet**: $50

**Pot odds**: $50 / $150 = 33.3%

**EV at exactly 33.3% equity**:
```
EV = (0.333 × $150) - (0.667 × $50)
   = $50 - $33.35
   ≈ $0
```

**When equity = pot odds, EV = 0** (break even)

## Multi-Street EV

### Considering Future Bets

Sometimes you need to account for future betting rounds.

### Example: Implied Odds Scenario

**Current situation**:
- Pot: $50
- Bet: $50
- Your equity: 20%
- **But**: If you hit, opponent will likely pay off another $100

**Current pot odds**: 33% (not enough!)

**But with implied odds**:
- Win 20% of the time: Win $200 ($100 current pot + $100 future bet)
- Lose 80% of the time: Lose $50

**EV Calculation**:
```
EV = (0.20 × $200) - (0.80 × $50)
   = $40 - $40
   = $0
```

**Break even** with implied odds! (May be worth a call)

## Comparing Multiple Options

### Example: Call, Raise, or Fold?

**Situation**:
- Pot: $100
- Opponent bets: $50
- Your hand: Strong draw (40% equity vs opponent's range)

#### Option 1: Fold
```
EV(fold) = $0
```

#### Option 2: Call
```
EV(call) = (0.40 × $150) - (0.60 × $50)
         = $60 - $30
         = +$30
```

#### Option 3: Raise to $150
Assume opponent folds 30% of the time, calls 70% of the time:

```
EV(raise) = (0.30 × $150) [fold equity]
          + (0.70 × 0.40 × $400) [win when called]
          - (0.70 × 0.60 × $150) [lose when called]

          = $45 + $112 - $63
          = +$94
```

**Best decision**: **Raise** (highest EV of $94)

This demonstrates how fold equity can make aggressive plays very profitable!

## Practice Problems

### Problem 1: Basic EV Calculation
**Pot**: $60
**Bet**: $30
**Your equity**: 25%

**What's the EV of calling?**

<details>
<summary>Answer</summary>

**If you call**:
- Win: 25% of the time, win $90
- Lose: 75% of the time, lose $30

**EV**:
```
EV = (0.25 × $90) - (0.75 × $30)
   = $22.50 - $22.50
   = $0
```

**Break even!** You're exactly at pot odds (33.3% needed).

Wait, let me recalculate pot odds:
- Pot odds = $30 / ($60 + $30 + $30) = $30 / $120 = 25%

Yes, you have exactly 25% equity and need exactly 25%, so EV = $0.
</details>

### Problem 2: 100 Trials Method
**Pot**: $40
**Bet**: $20
**Your equity**: 40%

**Use the 100 trials method to calculate EV.**

<details>
<summary>Answer</summary>

**Over 100 trials**:
- Win: 40 times
- Lose: 60 times

**Winnings**:
- 40 × $60 = $2,400

**Losses**:
- 60 × $20 = $1,200

**Net**:
- $2,400 - $1,200 = $1,200

**EV**:
- $1,200 / 100 = **+$12**

This is a great call!
</details>

### Problem 3: All-In EV
**Pot**: $150
**Opponent all-in**: $75
**Your equity**: 55%

**What's the EV of calling?**

<details>
<summary>Answer</summary>

**If you call**:
- Win: 55% of the time, win $225
- Lose: 45% of the time, lose $75

**EV**:
```
EV = (0.55 × $225) - (0.45 × $75)
   = $123.75 - $33.75
   = +$90
```

**Excellent call** worth $90 on average!
</details>

### Problem 4: Negative EV
**Pot**: $50
**Bet**: $100
**Your equity**: 20%

**What's the EV of calling?**

<details>
<summary>Answer</summary>

**If you call**:
- Win: 20% of the time, win $150
- Lose: 80% of the time, lose $100

**EV**:
```
EV = (0.20 × $150) - (0.80 × $100)
   = $30 - $80
   = -$50
```

**Terrible call!** You lose $50 on average each time.
</details>

### Problem 5: Fold Equity
**Pot**: $80
**You bet**: $60
**Opponent folds**: 40% of the time
**Your equity if called**: 30%

**What's the EV of betting?**

<details>
<summary>Answer</summary>

**If you bet**:
- Opponent folds 40%: Win $80
- Opponent calls 60%, you win 30%: Win $140
- Opponent calls 60%, you lose 70%: Lose $60

**EV**:
```
EV = (0.40 × $80) [fold equity]
   + (0.60 × 0.30 × $140) [win when called]
   - (0.60 × 0.70 × $60) [lose when called]

   = $32 + $25.20 - $25.20
   = +$32
```

**Profitable bet!** Even with only 30% equity when called, the fold equity makes this bet worth $32.
</details>

### Problem 6: Comparing Options
**Pot**: $100
**Your options**:
- **Fold**: EV = $0
- **Call $50**: 35% equity
- **Raise to $120**: Opponent folds 25%, if called you have 35% equity

**Which option has the highest EV?**

<details>
<summary>Answer</summary>

**EV(fold)** = $0

**EV(call)**:
```
EV = (0.35 × $150) - (0.65 × $50)
   = $52.50 - $32.50
   = +$20
```

**EV(raise)**:
```
EV = (0.25 × $100) [fold equity]
   + (0.75 × 0.35 × $370) [win when called]
   - (0.75 × 0.65 × $120) [lose when called]

   = $25 + $97.125 - $58.50
   = +$63.625
```

**Best option: Raise** with EV of +$63.63!

The fold equity from raising makes it much more profitable than calling.
</details>

## Common EV Mistakes

### Mistake 1: Forgetting About Investment
❌ **Wrong**: EV = Equity × Pot
✅ **Right**: EV = (Equity × Total Pot) - (Call Amount)

### Mistake 2: Ignoring Fold Equity
❌ **Wrong**: Only calculating equity when called
✅ **Right**: Including value from opponent folding

### Mistake 3: Confusing Pot Odds and EV
❌ **Wrong**: "I have pot odds, so EV is positive"
✅ **Right**: Check if equity exceeds pot odds requirement

### Mistake 4: Not Considering Future Streets
❌ **Wrong**: Only looking at current pot
✅ **Right**: Accounting for implied odds (future value)

## Advanced: EV of Bluffing

### Pure Bluff Example

**Pot**: $100
**Your hand**: Complete air (0% equity if called)
**You bet**: $75
**Opponent folds**: 50% of the time

**EV Calculation**:
```
EV = (0.50 × $100) [fold equity]
   + (0.50 × 0.00 × $175) [win when called = 0]
   - (0.50 × 1.00 × $75) [lose when called]

   = $50 + $0 - $37.50
   = +$12.50
```

**Profitable bluff!** Even with 0% equity, if opponent folds enough, bluffing makes money.

### Breakeven Fold Percentage

**Question**: How often does opponent need to fold for a bluff to break even?

**Formula**:
```
Breakeven Fold % = Bet Size / (Pot + Bet Size)
```

**Example**: Pot is $100, you bet $75
```
Breakeven = $75 / ($100 + $75) = 75/175 = 42.9%
```

**Interpretation**: Opponent needs to fold more than 43% of the time for your bluff to be profitable.

## Summary

1. **EV** = Expected average profit/loss per decision
2. **Positive EV** = Profitable (call/bet)
3. **Negative EV** = Unprofitable (fold)
4. **100 trials method** makes EV intuitive
5. **Consider fold equity** in aggressive plays
6. **Compare EV of all options** to find the best play

Mastering EV calculations transforms you from a player who "has a feeling" to a player who makes mathematically optimal decisions. Practice these calculations until they become second nature!
