# Equity Explained: Your Share of the Pot

## What Is Equity?

**Equity** is your percentage ownership of the pot based on your probability of winning the hand.

### The Ownership Metaphor

Think of the pot as a pie. Your equity is your slice of that pie.

**Example**: If you have 60% equity, you "own" 60% of the pot right now, even though you haven't won it yet.

## Why the Ownership Metaphor Works

Imagine playing the same hand 100 times:
- If you have 60% equity, you'll win about 60 times out of 100
- Over those 100 hands, you'll collect 60% of the total pot money
- **You own 60% of the pot in expectation**

## Calculating Equity: The Basics

### Formula
```
Your Equity = (Your Win Probability) × 100%
```

### Example 1: Coin Flip
**Situation**: You have A♠K♠ vs 8♥8♦

**Win probability**: ~47%

**Equity**: 47% of the pot

**If the pot is $100**: You own $47 of it (in expectation)

### Example 2: Dominating Hand
**Situation**: You have A♠A♥ vs K♣Q♣ (pre-flop)

**Win probability**: ~72%

**Equity**: 72% of the pot

**If the pot is $200**: You own $144 of it (in expectation)

### Example 3: Big Underdog
**Situation**: You have 7♣6♣ vs A♦A♠ (pre-flop)

**Win probability**: ~12%

**Equity**: 12% of the pot

**If the pot is $100**: You own $12 of it (in expectation)

## Equity in Multi-Way Pots

When more than two players are in the hand, equity is distributed among all players.

### Example: Three-Way Pot
**Pot**: $300

**Player A**: A♠A♥ (60% equity)
**Player B**: K♠Q♠ (25% equity)
**Player C**: 7♦6♦ (15% equity)

**Ownership**:
- Player A owns: $300 × 0.60 = $180
- Player B owns: $300 × 0.25 = $75
- Player C owns: $300 × 0.15 = $45
- **Total**: $180 + $75 + $45 = $300 ✓

Notice how all equities add up to 100% (or $300 in this case).

## How Equity Changes Throughout a Hand

Equity is dynamic—it changes with every card that's dealt.

### Example: Flush Draw on the Flop

**Your hand**: A♠9♠
**Opponent's hand**: A♦K♦
**Flop**: Q♠7♠2♣

#### Pre-flop Equity
- You (A♠9♠): ~25%
- Opponent (A♦K♦): ~75%

#### Flop Equity (after seeing the flop)
- You (flush draw): ~54%
- Opponent (top pair, top kicker): ~46%

**What happened?** The flop gave you 9 flush outs, dramatically increasing your equity!

### Example: Made Hand vs Draw on the Turn

**Your hand**: A♥K♥
**Opponent's hand**: 8♦7♦
**Board**: K♠9♦6♦4♣

#### Turn Equity
- You (top pair, top kicker): ~65%
- Opponent (flush draw + gutshot): ~35%

**One card to come**: Opponent has 9 flush outs + 3 gutshot outs (minus 1 for the 5♦ overlap) = ~11 outs

## Converting Outs to Equity

### Using the Rule of 2 and 4 (Simplified)

**On the flop** (two cards to come):
- Multiply outs by 4 to get approximate equity %

**On the turn** (one card to come):
- Multiply outs by 2 to get approximate equity %

### Example: Flush Draw on Flop
**Outs**: 9
**Equity**: 9 × 4 = **36%**

**Exact calculation**: 35% (very close!)

### Example: Open-Ended Straight Draw on Turn
**Outs**: 8
**Equity**: 8 × 2 = **16%**

**Exact calculation**: 17% (very close!)

See the "Rule of 2 and 4" guide for more details.

## Equity vs Pot Odds

Understanding the relationship between equity and pot odds is crucial for profitable poker decisions.

### The Key Principle
**You want to call when your equity is greater than the pot odds you're getting.**

### Example: Simple Decision

**Pot**: $100
**Opponent bets**: $50
**New pot**: $150
**Cost to call**: $50

**Pot odds**: $50 to win $150 = 1:3 = 25%

**Your hand**: Flush draw (9 outs on the turn)
**Your equity**: 9 × 2 = ~18%

**Decision**: **FOLD**
- You need 25% equity to call profitably
- You only have 18% equity
- Calling would lose money in the long run

### Example: Profitable Call

**Pot**: $100
**Opponent bets**: $25
**New pot**: $125
**Cost to call**: $25

**Pot odds**: $25 to win $125 = 1:5 = 20%

**Your hand**: Flush draw (9 outs on the turn)
**Your equity**: 9 × 2 = ~18%

**Wait, this seems close!** Let me recalculate...

Actually, you have 9 outs with two cards to come (on the flop), so:
**Your equity**: 9 × 4 = ~36%

**Decision**: **CALL**
- You need 20% equity to call profitably
- You have 36% equity
- Calling makes money in the long run!

## Fold Equity: Advanced Concept

**Fold equity** is the value you gain when your opponent folds, giving you 100% of the pot.

### Example: Bluffing with Fold Equity

**Pot**: $100
**Your hand**: 7♠2♦ (complete trash)
**Your actual equity (if called)**: ~15%

**You bet $50**

#### Scenario 1: Opponent Folds 50% of the Time
- 50% of the time: You win $100 immediately
- 50% of the time: You get called and win 15% of $150

**Expected value**:
- EV = (0.50 × $100) + (0.50 × 0.15 × $150) - $50
- EV = $50 + $11.25 - $50 = **+$11.25**

**Profitable bluff!** Even with terrible equity, you make money because your opponent folds enough.

#### Scenario 2: Opponent Never Folds
- You get called 100% of the time
- You win 15% of $150 = $22.50

**Expected value**:
- EV = $22.50 - $50 = **-$27.50**

**Bad bluff!** Without fold equity, you're just lighting money on fire.

## Equity Realization

**Equity realization** is how much of your theoretical equity you actually capture when you're out of position or lack skill.

### Why It Matters

**Theoretical equity**: Your percentage based purely on card probabilities

**Realized equity**: The percentage you actually win due to:
- Position
- Skill
- Hand reading ability
- Ability to navigate future streets

### Example: Out of Position

**Your hand**: A♠9♠ (flush draw on flop)
**Theoretical equity**: 36%

**But**:
- You're out of position
- Opponent can control pot size
- Opponent can bluff you off your hand
- You might not get paid when you hit

**Realized equity**: Maybe only 28-32%

**In position**: You realize closer to your full theoretical equity (maybe 34-36%)

## Key Takeaways

1. **Equity is ownership**: Your share of the pot based on win probability
2. **Equity changes**: Every card can dramatically shift equity
3. **Equity vs Pot Odds**: Call when equity > pot odds required
4. **Fold equity matters**: Opponents folding gives you additional value
5. **Position affects realization**: You capture more equity when in position

## Practice Problems

### Problem 1: Calculate Ownership
**Pot**: $200
**Your equity**: 35%
**How much do you own?**

<details>
<summary>Answer</summary>

$200 × 0.35 = **$70**

You own $70 of the $200 pot.
</details>

### Problem 2: Equity Decision
**Pot**: $80
**Opponent bets**: $40
**Your outs**: 12 (flush draw + overcard)
**Street**: Flop

**Should you call?**

<details>
<summary>Answer</summary>

**Pot odds**: $40 to win $120 = 33.3%
**Your equity**: 12 × 4 = 48%

**YES, CALL!** You have 48% equity and only need 33% to call profitably.
</details>

### Problem 3: Multi-Way Equity
**Pot**: $150
**Your equity**: 45%
**Opponent 1 equity**: 35%
**Opponent 2 equity**: 20%

**Verify these equities are correct:**

<details>
<summary>Answer</summary>

45% + 35% + 20% = **100%** ✓

Equities are correct. All equities in a pot must sum to 100%.

You own: $150 × 0.45 = $67.50
</details>

### Problem 4: Equity Change
**Your hand**: 8♥7♥
**Opponent hand**: A♠K♠
**Flop**: 9♥6♥2♣

**Before the flop, opponent had ~65% equity. What happened on this flop?**

<details>
<summary>Answer</summary>

You flopped:
- Open-ended straight draw (8 outs)
- Flush draw (9 outs)
- Minus overlap: 15 clean outs

**Your new equity**: ~60% (you're now favored!)

The flop completely flipped the equity. You went from a big underdog to a small favorite.
</details>

## Next Steps

Now that you understand equity, you're ready to:
- Learn **pot odds** in depth (comparing equity to pot odds)
- Master **expected value (EV)** calculations
- Understand **implied odds** (future equity from future bets)

Equity is the foundation of profitable poker decision-making!
