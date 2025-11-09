# Calculating Outs: A Complete Tutorial

## What Are Outs?

**Outs** are cards remaining in the deck that will improve your hand to (likely) the winning hand.

**Simple definition**: Outs are the cards you want to see on the next street.

## Why Outs Matter

Counting your outs accurately is the foundation of:
- Calculating your probability of winning
- Determining if a call is profitable
- Understanding pot odds and expected value
- Making better decisions under pressure

## The Systematic Approach to Counting Outs

### Step 1: Identify Your Current Hand
Look at your hole cards and the board. What do you have right now?

### Step 2: Determine What Hand You're Drawing To
What hand would make you confident you'll win?
- Flush?
- Straight?
- Two pair?
- Set?

### Step 3: Count the Cards That Complete That Hand
How many unseen cards would give you that hand?

### Step 4: Discount Outs (Advanced)
Are any of your outs likely to give your opponent a better hand?

## Common Drawing Situations

### Flush Draw (9 Outs)

**Situation**: You have two suited cards, and the flop shows two more of that suit.

**Your hand**: A♠ K♠
**Board**: Q♠ 7♠ 2♦

**How to count**:
- There are 13 cards of each suit
- You have 2 spades (A♠ K♠)
- Board has 2 spades (Q♠ 7♠)
- Total spades accounted for: 4
- **Outs: 13 - 4 = 9 spades**

**Visual exercise**:
```
Known spades: A♠ K♠ Q♠ 7♠
Unknown spades: K♠ J♠ 10♠ 9♠ 8♠ 6♠ 5♠ 4♠ 3♠
Count: 9 outs
```

### Open-Ended Straight Draw (8 Outs)

**Situation**: You need a card on either end to complete your straight.

**Your hand**: 9♥ 8♥
**Board**: 7♣ 6♠ 2♦

**How to count**:
- You need a Ten or a Five to complete the straight
- Tens in the deck: 4 (T♠, T♥, T♦, T♣)
- Fives in the deck: 4 (5♠, 5♥, 5♦, 5♣)
- **Outs: 4 + 4 = 8 cards**

**Visual exercise**:
```
Cards that make a straight: T-9-8-7-6 or 9-8-7-6-5
Tens: T♠ T♥ T♦ T♣
Fives: 5♠ 5♥ 5♦ 5♣
Count: 8 outs
```

### Gutshot Straight Draw (4 Outs)

**Situation**: You need a card in the middle to complete your straight.

**Your hand**: 9♦ 8♦
**Board**: J♠ 7♣ 2♥

**How to count**:
- You need a Ten to make J-T-9-8-7
- Tens in the deck: 4 (T♠, T♥, T♦, T♣)
- **Outs: 4 cards**

**Visual exercise**:
```
Cards that make a straight: J-T-9-8-7
Tens: T♠ T♥ T♦ T♣
Count: 4 outs
```

### Two Overcards (6 Outs)

**Situation**: You have two cards higher than the board, and pairing either would likely give you the best hand.

**Your hand**: A♣ K♦
**Board**: 9♠ 7♥ 3♦

**How to count**:
- Aces that pair your ace: 3 (A♠, A♥, A♦)
- Kings that pair your king: 3 (K♠, K♥, K♣)
- **Outs: 3 + 3 = 6 cards**

**Note**: This assumes your opponent doesn't already have a pair higher than your overcards or a made hand like two pair.

### Set Draw (2 Outs)

**Situation**: You have a pocket pair and need to hit your set.

**Your hand**: 8♠ 8♥
**Board**: K♣ 9♦ 4♠

**How to count**:
- Eights that make a set: 2 (8♦, 8♣)
- **Outs: 2 cards**

**Visual exercise**:
```
Cards that make a set: 8♦ 8♣
Count: 2 outs
```

## Combining Multiple Draws

### Flush Draw + Overcard (12 Outs)

**Your hand**: A♠ K♠
**Board**: Q♠ 7♠ 5♦

**How to count**:
- Flush outs: 9 spades
- Overcard outs: 3 aces + 3 kings = 6 cards
- **But wait!** A♠ and K♠ are already counted in flush outs
- Actual overcard outs: (3 aces - 1 A♠) + (3 kings - 1 K♠) = 4
- **Total outs: 9 + 4 = 13 outs**

**Important**: Don't double-count cards!

### Flush Draw + Straight Draw (15 Outs)

**Your hand**: J♠ T♠
**Board**: 9♠ 8♣ 2♠

**How to count**:
- Flush outs: 9 spades
- Straight outs: 4 queens + 4 sevens = 8 cards
- **But wait!** Q♠ and 7♠ are already counted in flush outs
- Actual straight outs: (4 queens - 1 Q♠) + (4 sevens - 1 7♠) = 6
- **Total outs: 9 + 6 = 15 outs**

This is called a "monster draw"!

## Discounting Outs (Advanced Concept)

Not all outs are "clean." Sometimes an out improves your hand but gives your opponent an even better hand.

### Example: Flush Draw vs Set

**Your hand**: A♠ 9♠
**Board**: K♠ 7♠ 7♣

**Initial count**: 9 flush outs

**But consider**:
- Your opponent likely has a 7 (trips) or K-7 (full house)
- If a 7♠ comes (one of your flush cards), it gives opponent a full house or quads
- The 7♠ is a "tainted out"

**Discounted outs**: 9 - 1 = 8 outs

**Rule of thumb**: When the board is paired and you're drawing to a flush, discount your flush outs by 1-2 cards.

### Example: Straight Draw on a Flush Board

**Your hand**: J♥ T♥
**Board**: 9♠ 8♠ 2♠

**Initial count**: 8 straight outs (4 queens + 4 sevens)

**But consider**:
- The Q♠ and 7♠ would complete a flush for anyone holding two spades
- These might not be clean wins

**Discounted outs**: 8 - 2 = 6 "clean" outs (plus 2 "dirty" outs)

## Practice Exercises

Count the outs for each scenario:

### Exercise 1: Basic Flush Draw
**Your hand**: 7♦ 6♦
**Board**: K♦ J♦ 3♣

<details>
<summary>Answer</summary>

**9 outs** (9 remaining diamonds)
</details>

### Exercise 2: Open-Ended Straight Draw
**Your hand**: Q♥ J♣
**Board**: T♠ 9♦ 2♥

<details>
<summary>Answer</summary>

**8 outs** (4 kings + 4 eights)
</details>

### Exercise 3: Gutshot
**Your hand**: A♠ Q♥
**Board**: J♦ T♠ 5♣

<details>
<summary>Answer</summary>

**4 outs** (4 kings for the straight)

Note: You also have 6 overcard outs (3 aces + 3 queens), but those might not be good if your opponent has a made straight already.
</details>

### Exercise 4: Combo Draw
**Your hand**: 8♥ 7♥
**Board**: 9♥ 6♦ 2♥

<details>
<summary>Answer</summary>

**15 outs**
- Flush: 9 hearts
- Straight: (4 tens - 1 T♥) + (4 fives - 1 5♥) = 6
- Total: 9 + 6 = 15 outs

This is a massive draw!
</details>

### Exercise 5: Two Pair Draw
**Your hand**: A♣ K♠
**Board**: K♦ 9♥ 5♠

**Question**: How many outs to improve to two pair or better?

<details>
<summary>Answer</summary>

**6 outs**
- Aces for two pair: 3 aces
- Kings for trips: 2 kings (K♥, K♣)
- Note: We already have one king, so only 2 kings left
- Wait, we actually have top pair already!
- To improve: 3 aces (for two pair) + 2 kings (for trips) = 5 outs

Actually, **5 outs** is the correct answer.
</details>

### Exercise 6: Advanced - Discounting Outs
**Your hand**: Q♠ J♠
**Board**: T♠ 9♠ 9♣

**Question**: How many clean outs do you have?

<details>
<summary>Answer</summary>

**Initial count**:
- Flush: 9 spades
- Straight: (4 kings - 1 K♠) + (4 eights - 1 8♠) = 6
- Total: 15 outs

**Discounting**:
- The 9♠ gives you a flush but opponent a full house/quads (if they have a 9)
- Discount: 15 - 1 = **14 outs**

In reality, you have about 14 clean outs. This is still a massive draw!
</details>

## Common Mistakes When Counting Outs

### Mistake 1: Double-Counting
❌ **Wrong**: "I have 9 flush outs plus 4 outs to pair my ace, so 13 outs"
(When one of the flush cards is an ace)

✅ **Right**: "I have 9 flush outs plus 3 non-flush aces, so 12 outs"

### Mistake 2: Counting Opponent's Outs
❌ **Wrong**: Counting cards that would improve your hand but give the opponent a better hand

✅ **Right**: Discount outs that are "tainted"

### Mistake 3: Not Accounting for Seen Cards
❌ **Wrong**: "There are 4 kings in the deck, so I have 4 outs"
(When you've already seen a king on the board)

✅ **Right**: Count only unseen cards

### Mistake 4: Overvaluing Weak Draws
❌ **Wrong**: Counting 6 overcard outs when opponent likely has a made hand

✅ **Right**: Only count outs to hands that will actually win

## Quick Reference: Common Outs

| Draw Type | Outs | Example |
|-----------|------|---------|
| Flush draw | 9 | Two suited cards + 2 on board |
| Open-ended straight | 8 | Consecutive cards, need either end |
| Two overcards | 6 | AK on a low board |
| Gutshot straight | 4 | Need one specific rank |
| One pair to two pair | 5 | Need to pair your kicker or make trips |
| Pocket pair to set | 2 | Need one of two remaining cards |

## Summary

1. **Systematically count**: Identify your draw, count all cards that complete it
2. **Don't double-count**: If a card fills multiple draws, count it once
3. **Discount when needed**: Tainted outs don't count as full outs
4. **Practice regularly**: The more you practice, the faster you'll count at the table

Once you've mastered counting outs, you're ready to learn about converting outs to probabilities using the **Rule of 2 and 4**.
