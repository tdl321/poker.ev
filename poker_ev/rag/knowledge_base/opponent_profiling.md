# Opponent Profiling and Player Types

## The Four Player Types

### 1. Tight-Passive (Rock/Nit)
**Characteristics**:
- Plays very few hands (5-15%)
- Rarely raises or bets
- Calls and checks frequently
- Folds to aggression

**Exploitative Strategy**:
- **Steal their blinds**: They fold too much
- **Don't bluff them**: They only call with good hands
- **Fold when they bet**: They usually have the goods
- **Avoid paying them off**: When they raise, they have it

### 2. Tight-Aggressive (TAG)
**Characteristics**:
- Plays premium hands (15-25%)
- Bets and raises often
- Strong post-flop player
- Hardest to play against

**Exploitative Strategy**:
- **Play straightforward**: They'll notice patterns
- **3-bet bluff occasionally**: They can fold
- **Trap with monsters**: Let them bet
- **Avoid marginal spots**: They make good decisions

### 3. Loose-Passive (Calling Station)
**Characteristics**:
- Plays too many hands (40-60%)
- Rarely raises
- Calls too much
- Won't fold draws

**Exploitative Strategy**:
- **Value bet relentlessly**: They pay you off
- **DON'T BLUFF**: They won't fold
- **Bet big with strong hands**: Extract maximum value
- **Avoid thin value bets**: They might have random two pair

### 4. Loose-Aggressive (LAG/Maniac)
**Characteristics**:
- Plays many hands (35-50%)
- Bets and raises frequently
- Difficult to put on a hand
- High variance

**Exploitative Strategy**:
- **Trap them**: Let them bet for you
- **3-bet/4-bet premium hands**: They'll pay you off
- **Call down lighter**: They bluff often
- **Stay patient**: Wait for good spots
- **Don't get tilted**: Expect swings

## VPIP and PFR Stats

### VPIP (Voluntarily Put Money In Pot)
- **Tight**: < 20%
- **Normal**: 20-30%
- **Loose**: > 30%
- **Very Loose**: > 40%

### PFR (Pre-Flop Raise)
- **Passive**: < 10%
- **Normal**: 15-20%
- **Aggressive**: > 25%

### VPIP/PFR Combinations
- **20/18**: Solid TAG player
- **30/25**: Aggressive regular
- **40/10**: Loose-passive (calling station)
- **12/10**: Tight-passive (rock/nit)
- **45/35**: Loose-aggressive (LAG/maniac)

## Betting Patterns

### C-Bet Frequency
- **High (70%+)**: Bluffs a lot, float or raise
- **Medium (50-60%)**: Balanced, play standard
- **Low (< 40%)**: Only bets strong hands, fold to bets

### 3-Bet Frequency
- **High (8%+)**: 3-betting light, 4-bet strong hands
- **Medium (4-7%)**: Balanced 3-betting
- **Low (< 3%)**: Only 3-bets premiums, fold to 3-bets

### Fold to 3-Bet
- **High (70%+)**: 3-bet them relentlessly
- **Medium (50-65%)**: 3-bet for value
- **Low (< 45%)**: Don't 3-bet bluff, value only

## Timing Tells

### Quick Actions
- **Instant check**: Usually weak, wants to see next card
- **Instant call**: Drawing hand or medium strength
- **Instant bet**: Strong hand or automated bluff

### Slow Actions
- **Long check**: Often strong, thinking about check-raise
- **Long call**: Marginal hand, weighing pot odds
- **Long bet**: Bluffing or value betting thin

## Bet Sizing Tells

### Small Bets (25-40% pot)
- **Weak players**: Weak hand or drawing
- **Strong players**: Inducing call or polarized range

### Medium Bets (50-75% pot)
- **Standard c-bet**: Could be anything
- **Value bet**: Strong but not nuts
- **Bluff**: Balanced bet sizing

### Large Bets (100%+ pot)
- **Weak players**: Nuts or bluff (polarized)
- **Strong players**: Balanced, could be value or bluff
- **Multi-way**: Usually very strong

### Overbet (150%+ pot)
- **Nuts or air**: Highly polarized
- **Fold equity**: Trying to push you out
- **Unbalanced players**: Often the nuts

## Adjusting to Table Dynamics

### Tight Table
- **Steal more**: Everyone folding too much
- **Bluff more**: Opponents respect bets
- **Value bet thinner**: They'll fold

### Loose Table
- **Tighten up**: Play premium hands
- **Don't bluff**: They won't fold
- **Value bet bigger**: They'll pay you off

### Aggressive Table
- **Trap more**: Let them bet for you
- **3-bet stronger**: They're opening wide
- **Call down lighter**: They're bluffing often

### Passive Table
- **Bet more**: They won't fight back
- **Value bet often**: They'll call
- **Don't slowplay**: Build the pot yourself

## Specific Opponent Adjustments

### Against Calling Stations (AI: Call Agent)
- ✅ Value bet, value bet, value bet
- ✅ Make big bets with strong hands
- ✅ Check down marginal hands
- ❌ DON'T BLUFF
- ❌ Don't slow play

### Against Maniacs (AI: Aggressive Agent)
- ✅ Check-raise for value
- ✅ Call down with medium hands
- ✅ 3-bet premiums for value
- ✅ Let them bluff off chips
- ❌ Don't fight fire with fire
- ❌ Don't bluff them

### Against Rocks (AI: Tight Agent)
- ✅ Steal their blinds constantly
- ✅ Fold when they show aggression
- ✅ Bluff them off marginal hands
- ❌ Don't pay them off
- ❌ Don't value bet thin against them

### Against Randoms (AI: Random Agent)
- ✅ Play solid ABC poker
- ✅ Value bet strong hands
- ✅ Avoid fancy plays
- ❌ Don't try to exploit randomness
- ❌ Just play fundamentals

## Tracking Opponent Tendencies

### Pre-Flop Tendencies
- What hands do they open from each position?
- How often do they 3-bet?
- Do they fold to 3-bets?
- How do they play in blinds?

### Post-Flop Tendencies
- C-bet frequency by position
- Response to c-bets (fold, call, raise)
- Turn and river aggression
- Showdown hand strengths

### Specific Hand History
- Did they bluff in a big pot?
- What hands do they value bet?
- What hands do they check-raise?
- Do they slow-play strong hands?

## Exploiting Common Leaks

### Leak 1: Over-folding to c-bets
- **Exploit**: C-bet 100% of flops

### Leak 2: Never folding to c-bets
- **Exploit**: Only c-bet strong hands

### Leak 3: Too much pre-flop calling
- **Exploit**: Raise more often, value bet more

### Leak 4: Predictable bet sizing
- **Exploit**: Know their range from bet size

### Leak 5: Playing face-up
- **Exploit**: Know exactly where you stand

## Building a Player Profile

For each opponent, track:
1. **Pre-flop stats**: VPIP, PFR, 3-bet%
2. **Post-flop tendencies**: C-bet, fold to c-bet, aggression
3. **Showdown hands**: What did they have?
4. **Notable hands**: Bluffs, big pots, mistakes
5. **Tilt indicators**: Do they steam after bad beats?

## Table Image and Adjusting

### Your Image is Tight
- **Exploit**: Bluff more, they'll fold
- **Downside**: Less value when you bet

### Your Image is Loose
- **Exploit**: Value bet more, they'll call
- **Downside**: Less successful bluffs

### Your Image is Aggressive
- **Exploit**: Get action on big hands
- **Downside**: Get 3-bet more, harder to steal

### Your Image is Passive
- **Exploit**: See cheap flops, fly under radar
- **Downside**: Don't get paid off, get bullied
