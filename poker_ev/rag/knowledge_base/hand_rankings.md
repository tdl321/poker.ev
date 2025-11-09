# Texas Hold'Em Hand Rankings

## Hand Strength Hierarchy (Best to Worst)

### 1. Royal Flush
- **Definition**: A, K, Q, J, 10, all of the same suit
- **Example**: A♠ K♠ Q♠ J♠ 10♠
- **Probability**: 0.000154% (1 in 649,740)
- **Unbeatable**: This is the absolute best hand in poker

### 2. Straight Flush
- **Definition**: Five consecutive cards of the same suit
- **Example**: 9♥ 8♥ 7♥ 6♥ 5♥
- **Probability**: 0.00139% (1 in 72,193)
- **Note**: A-2-3-4-5 is the lowest straight flush (wheel)

### 3. Four of a Kind (Quads)
- **Definition**: Four cards of the same rank
- **Example**: K♠ K♥ K♦ K♣ A♠
- **Probability**: 0.0240% (1 in 4,165)
- **Kicker**: Fifth card breaks ties between equal quads

### 4. Full House (Boat)
- **Definition**: Three of a kind plus a pair
- **Example**: 8♠ 8♥ 8♦ 3♣ 3♦
- **Probability**: 0.1441% (1 in 694)
- **Ranking**: Higher trips beat lower trips (888-33 beats 777-AA)

### 5. Flush
- **Definition**: Five cards of the same suit, not in sequence
- **Example**: A♦ J♦ 9♦ 6♦ 2♦
- **Probability**: 0.1965% (1 in 509)
- **Note**: If multiple players have flushes, highest card wins

### 6. Straight
- **Definition**: Five consecutive cards of different suits
- **Example**: 10♠ 9♥ 8♦ 7♣ 6♠
- **Probability**: 0.3925% (1 in 255)
- **Note**: Ace can be high (A-K-Q-J-10) or low (A-2-3-4-5)

### 7. Three of a Kind (Trips/Set)
- **Definition**: Three cards of the same rank
- **Example**: Q♠ Q♥ Q♦ K♠ 7♣
- **Probability**: 2.1128% (1 in 47)
- **Terminology**: "Set" = pocket pair + board card, "Trips" = two on board

### 8. Two Pair
- **Definition**: Two different pairs
- **Example**: J♠ J♥ 5♦ 5♣ A♠
- **Probability**: 4.7539% (1 in 21)
- **Kicker**: Fifth card breaks ties

### 9. One Pair
- **Definition**: Two cards of the same rank
- **Example**: 9♠ 9♥ K♦ 7♣ 3♠
- **Probability**: 42.26% (1 in 2.4)
- **Common**: Most common made hand at showdown

### 10. High Card
- **Definition**: No pair, highest card wins
- **Example**: A♠ K♥ 8♦ 5♣ 2♠ (Ace-high)
- **Probability**: 50.12%
- **Note**: Compare highest card, then second-highest if tied

## Probability Comparisons

### How Often Will You Be Dealt Each Hand Type?

Understanding how rare each hand is helps you appreciate their value:

| Hand Type | Probability (5 cards) | Frequency | Practical Meaning |
|-----------|----------------------|-----------|-------------------|
| Royal Flush | 0.000154% | 1 in 649,740 | Once in a lifetime |
| Straight Flush | 0.00139% | 1 in 72,193 | Extremely rare |
| Four of a Kind | 0.024% | 1 in 4,165 | Very rare |
| Full House | 0.144% | 1 in 694 | Rare |
| Flush | 0.197% | 1 in 509 | Uncommon |
| Straight | 0.392% | 1 in 255 | Uncommon |
| Three of a Kind | 2.11% | 1 in 47 | Once per ~50 hands |
| Two Pair | 4.75% | 1 in 21 | Several times per session |
| One Pair | 42.26% | 1 in 2.4 | Very common |
| High Card | 50.12% | 1 in 2 | Most common |

**Key insight**: You'll see high card or one pair about 92% of the time at showdown!

### Pre-Flop Probabilities

How likely are you to be dealt specific starting hands?

| Hand | Probability | Frequency | Example |
|------|-------------|-----------|---------|
| Any specific suited hand | 0.045% | 1 in 221 | A♠K♠ |
| Any specific offsuit hand | 0.136% | 1 in 73 | A♥K♦ |
| Any pocket pair | 5.88% | 1 in 17 | Any pair |
| Specific pocket pair | 0.45% | 1 in 221 | A-A |
| Any two suited cards | 23.5% | 1 in 4.3 | Any suited |
| Premium pairs (J-J+) | 2.1% | 1 in 48 | J-J to A-A |
| A-K (any) | 1.2% | 1 in 83 | AK suited or offsuit |
| A-A or K-K | 0.9% | 1 in 111 | Top two pairs |

**Practical tip**: You'll get A-A about once every 221 hands (roughly once every 3-4 hours of live play).

### Flop Probabilities: How Often Will You Improve?

Starting with different hand types, here's how often you'll hit by the flop:

#### With a Pocket Pair

| Result | Probability | Frequency |
|--------|-------------|-----------|
| Flop a set | 11.8% | 1 in 8.5 |
| Flop quads | 0.24% | 1 in 408 |
| Flop full house | 0.73% | 1 in 136 |
| Improve to set or better | 12% | 1 in 8.3 |

**Key insight**: Set mining requires good implied odds because you only flop a set ~12% of the time.

#### With Suited Cards

| Result | Probability | Frequency |
|--------|-------------|-----------|
| Flop a flush | 0.84% | 1 in 118 |
| Flop a flush draw | 10.9% | 1 in 9.2 |
| Flop at least a flush draw | 11.8% | 1 in 8.5 |

**Key insight**: Flush draws are much more common than made flushes!

#### With Connectors (e.g., 9-8)

| Result | Probability | Frequency |
|--------|-------------|-----------|
| Flop a straight | 1.3% | 1 in 77 |
| Flop open-ended straight draw | 9.8% | 1 in 10.2 |
| Flop any straight draw | 19% | 1 in 5.3 |

#### With Unpaired Cards (e.g., A-K)

| Result | Probability | Frequency |
|--------|-------------|-----------|
| Flop top pair | 29% | 1 in 3.4 |
| Flop any pair | 32% | 1 in 3.1 |
| Flop two pair | 2% | 1 in 49 |
| Flop trips | 1.35% | 1 in 74 |

**Key insight**: With A-K, you'll miss the flop (no pair) about 2 out of 3 times!

### Common Pre-Flop Matchups (Head to Head)

Understanding these matchups helps you make better all-in decisions:

#### Pair vs Pair (Higher vs Lower)

| Matchup | Higher Pair | Lower Pair |
|---------|-------------|------------|
| A-A vs K-K | 82% | 18% |
| K-K vs Q-Q | 82% | 18% |
| Q-Q vs J-J | 82% | 18% |
| J-J vs T-T | 82% | 18% |
| T-T vs 9-9 | 81% | 19% |
| 5-5 vs 2-2 | 81% | 19% |

**Pattern**: Higher pocket pair has about 80-82% equity.

#### Pair vs Two Overcards (The "Classic Race")

| Matchup | Pair | Overcards |
|---------|------|-----------|
| 2-2 vs A-K | 52% | 48% |
| 6-6 vs A-K | 54% | 46% |
| 9-9 vs A-K | 54% | 46% |
| J-J vs A-K | 57% | 43% |
| Q-Q vs A-K | 57% | 43% |

**Key insight**: Low pairs are slight favorites vs overcards (called a "coin flip" or "race").

#### Pair vs Lower Overcards

| Matchup | Pair | Lower Cards |
|---------|------|-------------|
| A-A vs K-Q | 85% | 15% |
| K-K vs Q-J | 82% | 18% |
| Q-Q vs J-T | 77% | 23% |
| J-J vs T-9 | 77% | 23% |

**Pattern**: Pairs dominate when they're higher than opponent's cards.

#### Domination Situations

| Matchup | Dominating | Dominated |
|---------|------------|-----------|
| A-K vs A-Q | 74% | 26% |
| A-K vs A-J | 75% | 25% |
| A-K vs K-Q | 73% | 27% |
| A-Q vs A-J | 74% | 26% |
| K-Q vs K-J | 73% | 27% |

**Key insight**: When you share a card with opponent but have a better kicker, you're a huge favorite (~74%).

#### Suited vs Offsuit (Same Ranks)

| Matchup | Suited | Offsuit |
|---------|--------|---------|
| A♠K♠ vs A♥K♦ | 58% | 42% |
| J♠T♠ vs J♥T♦ | 58% | 42% |
| 7♠6♠ vs 7♥6♦ | 58% | 42% |

**Pattern**: Suited hands have about 3% better equity (from flush potential).

### Turn and River Improvement Probabilities

If you have a draw on the flop, here's how likely you are to complete it:

#### From the Flop

| Draw Type | Outs | Flop→River | Turn→River | Example |
|-----------|------|------------|------------|---------|
| Gutshot | 4 | 16.5% | 8.7% | Need one specific rank |
| Two overcards | 6 | 24% | 13% | A-K on low board |
| Open-ended straight | 8 | 31.5% | 17.4% | 9-8 on 7-6-X |
| Flush draw | 9 | 35% | 19.6% | Two suited + two on board |
| Flush draw + pair | 12 | 45% | 26% | Flush draw + pair outs |
| Flush + OESD | 15 | 54% | 33% | Monster draw |

**How to use**:
- **Flop→River**: Percentage to complete by river (seeing both turn and river)
- **Turn→River**: Percentage to complete on river only (if you missed the turn)

### Hand vs Hand Post-Flop Scenarios

#### Made Hand vs Draw

| Situation | Made Hand | Drawing Hand | Notes |
|-----------|-----------|--------------|-------|
| Top pair vs flush draw | 55% | 45% | Draw is close |
| Overpair vs OESD | 67% | 33% | Pair is favorite |
| Two pair vs flush draw | 71% | 29% | Two pair ahead |
| Set vs flush draw | 72% | 28% | Set is big favorite |

#### Draw vs Draw

| Situation | Better Draw | Worse Draw | Notes |
|-----------|-------------|------------|-------|
| Flush draw vs gutshot | 62% | 38% | Flush draw much better |
| OESD vs gutshot | 65% | 35% | OESD significantly ahead |
| Better flush draw vs worse | 58% | 42% | Higher cards matter |

#### Made Hand vs Made Hand

| Situation | Better Hand | Worse Hand | Notes |
|-----------|-------------|------------|-------|
| Top pair vs middle pair | 84% | 16% | Dominated pair |
| Overpair vs underpair | 82% | 18% | Similar to pre-flop |
| Set vs top two pair | 78% | 22% | Set is favorite |
| Flush vs straight | 84% | 16% | Flush dominates |

### Probability of Improving to Specific Hands

From the flop onward, here's how likely you are to improve to various strong hands:

#### From Two Pair to Full House

- **By river**: 16.5% (4 outs: 2 for trips, 2 for other pair)
- **On turn only**: 8.7%

#### From Set to Full House or Quads

- **By river**: 28.3% (7 outs: 6 for boat, 1 for quads)
- **On turn only**: 15.2%

**Why sets are strong**: They improve to full house or quads nearly 1 in 3.5 times!

#### From Flush Draw to Flush

- **By river**: 35% (9 outs)
- **On turn only**: 19.6%

#### From OESD to Straight

- **By river**: 31.5% (8 outs)
- **On turn only**: 17.4%

## Hand Equity Concepts

### Drawing Hands

#### Open-Ended Straight Draw (OESD)
- **Example**: You have 9-8, board is 7-6-2
- **Outs**: 8 cards (four 10s, four 5s)
- **Equity vs. one pair**: ~31% (turn + river)
- **Turn equity**: ~17%

#### Flush Draw
- **Example**: You have A♠ K♠, board is Q♠ 7♠ 2♥
- **Outs**: 9 cards (remaining spades)
- **Equity vs. one pair**: ~35% (turn + river)
- **Turn equity**: ~19%

#### Combo Draw (Straight + Flush)
- **Example**: You have 10♠ 9♠, board is 8♠ 7♠ 2♥
- **Outs**: 15 cards (9 spades + 6 straight cards)
- **Equity vs. one pair**: ~54%
- **Very powerful**: Often ahead of top pair

### Made Hand Strengths

#### Top Pair Top Kicker (TPTK)
- **Example**: You have A-K, board is K-7-2
- **Typical equity vs. random hand**: 70-80%
- **Vulnerable to**: Two pair, sets, draws

#### Overpair
- **Example**: You have Q-Q, board is 10-8-3
- **Typical equity**: 75-85% vs. one pair
- **Play**: Usually bet for value and protection

#### Set (Three of a Kind)
- **Example**: You have 7-7, board is 7-K-2
- **Typical equity**: 85-95% vs. one pair
- **Disguised**: Very strong but hidden

## Pre-Flop Hand Strength

### Premium Hands (Top 2%)
- **Pairs**: A-A, K-K, Q-Q, J-J
- **Suited**: A-Ks (Ace-King suited)
- **Strategy**: Raise/3-bet from any position

### Strong Hands (Top 5%)
- **Pairs**: 10-10, 9-9
- **Suited**: A-Qs, A-Js, K-Qs
- **Unsuited**: A-K
- **Strategy**: Raise from most positions

### Playable Hands (Top 15%)
- **Pairs**: 8-8 down to 2-2
- **Suited**: A-10s, K-Js, K-10s, Q-Js, J-10s
- **Suited Connectors**: 9-8s, 8-7s, 7-6s
- **Strategy**: Position-dependent, raise from late position

### Speculative Hands
- **Small Pairs**: 2-2 to 6-6 (set mining)
- **Suited Connectors**: 5-4s, 6-5s, etc.
- **Strategy**: Cheap to see flops, implied odds important

## Position-Based Hand Selection

### Early Position (UTG, UTG+1)
- **Play**: Top 10-15% of hands
- **Reason**: Many players act after you

### Middle Position (MP, HJ)
- **Play**: Top 20-25% of hands
- **Reason**: Better position, fewer players behind

### Late Position (CO, Button)
- **Play**: Top 35-40% of hands
- **Reason**: Best position, act last post-flop

### Blinds (SB, BB)
- **Play**: Defend based on pot odds
- **Reason**: Already invested money, but worst position
