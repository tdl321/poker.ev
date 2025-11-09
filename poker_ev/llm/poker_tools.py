"""
Poker Advisor Tools for LangChain Agent

Defines specialized tools that the poker advisor agent can use to:
- Search poker strategy knowledge base (Pinecone RAG)
- Access current game state
- Calculate pot odds
- Estimate hand strength
- Analyze position advantage
"""

from langchain.tools import tool
from typing import List
import logging

logger = logging.getLogger(__name__)


class PokerTools:
    """
    Collection of poker-specific tools for LangChain agent

    These tools give the agent capabilities to:
    - Search poker knowledge base via Pinecone
    - Get real-time game state information
    - Perform mathematical calculations (pot odds)
    - Evaluate poker hands and positions
    """

    def __init__(self, pinecone_store, game_context_provider=None, decision_tracker=None, hand_history=None):
        """
        Initialize poker tools

        Args:
            pinecone_store: PineconePokerStore instance for RAG
            game_context_provider: GameContextProvider for current game state
            decision_tracker: DecisionTracker instance for decision history (optional)
            hand_history: HandHistory instance for searching past hands (optional)
        """
        self.pinecone_store = pinecone_store
        self.game_context_provider = game_context_provider
        self.decision_tracker = decision_tracker
        self.hand_history = hand_history

    def create_tools(self) -> List:
        """
        Create all poker tools for the agent using @tool decorator

        Returns:
            List of LangChain tool functions
        """
        # Create closures over self to access store, context provider, decision tracker, and hand history
        pinecone_store = self.pinecone_store
        game_context_provider = self.game_context_provider
        decision_tracker = self.decision_tracker
        hand_history = self.hand_history

        @tool
        def search_poker_knowledge(query: str) -> str:
            """Search the poker strategy knowledge base for information about hand rankings, position strategy, pot odds, and opponent profiling. Use this when the user asks about general poker concepts or strategy."""
            try:
                # Use Pinecone to search poker strategy
                context = pinecone_store.search_as_context(query, k=2)

                if not context or "No relevant" in context:
                    return "No specific poker strategy found for this query. Use general poker principles."

                return context
            except Exception as e:
                logger.error(f"Error searching knowledge base: {e}")
                return f"Knowledge base search failed: {str(e)}"

        @tool
        def get_game_state() -> str:
            """[DEPRECATED - Rarely needed] Get the current poker game state.

            ⚠️ NOTE: Game state is AUTOMATICALLY provided in every user query in a [CURRENT GAME STATE] block.
            You should read the auto-provided state from the user message instead of calling this tool.

            This tool is only useful in special cases where you need to refresh the state or access it programmatically.
            For normal advice, always use the game state already in the user's message."""
            if not game_context_provider:
                return "No active game state available"

            try:
                # Get formatted game state
                game_context = game_context_provider.get_full_context()
                return game_context
            except Exception as e:
                logger.error(f"Error getting game state: {e}")
                return f"Could not retrieve game state: {str(e)}"

        @tool
        def calculate_pot_odds(input_str: str) -> str:
            """Calculate pot odds, required equity, and Expected Value (EV) for poker decisions.

            Input formats:
            1. 'pot_size,bet_to_call' - Shows pot odds and required equity only
            2. 'pot_size,bet_to_call,equity' - Also calculates EV and profitability
            3. 'pot_size,bet_to_call,equity,teach' - Full teaching mode with step-by-step explanations

            Examples:
            - '150,30' → Pot odds for $150 pot, $30 to call
            - '150,30,35' → Same + EV calculation with 35% win probability
            - '150,30,35,teach' → Teaching mode with detailed probability explanations

            Returns: Pot odds ratio, required equity %, and EV analysis (if equity provided).
            Teaching mode includes detailed probability breakdowns and learning notes.
            Use when evaluating whether to call a bet. Always get pot/bet from game state."""
            try:
                # Parse input
                parts = input_str.strip().split(',')
                if len(parts) < 2 or len(parts) > 4:
                    return "Invalid input. Use: pot_size,bet_to_call[,equity][,teach] (e.g., '100,20' or '100,20,35' or '100,20,35,teach')"

                pot_size = float(parts[0].strip())
                bet_to_call = float(parts[1].strip())

                # Check for teaching mode
                teaching_mode = False
                equity = None

                if len(parts) >= 3:
                    if parts[-1].strip().lower() == 'teach':
                        teaching_mode = True
                        if len(parts) == 4:
                            equity = float(parts[2].strip())
                    else:
                        equity = float(parts[2].strip())
                        if len(parts) == 4 and parts[3].strip().lower() == 'teach':
                            teaching_mode = True

                if bet_to_call == 0:
                    return "No bet to call - you can check for free (no pot odds needed, EV = $0)"

                if pot_size < 0 or bet_to_call < 0:
                    return "Invalid input: pot size and bet must be positive numbers"

                if equity is not None and (equity < 0 or equity > 100):
                    return "Invalid equity: must be between 0 and 100%"

                # Calculate pot odds
                total_pot = pot_size + bet_to_call
                pot_odds_ratio = total_pot / bet_to_call
                pot_odds_percentage = (bet_to_call / total_pot) * 100
                required_equity = pot_odds_percentage

                # Build result based on teaching mode
                if teaching_mode:
                    result_parts = [
                        "📊 POT ODDS & EXPECTED VALUE ANALYSIS",
                        "",
                        "**Step 1: Identify the Numbers**",
                        f"• Bet you need to call: ${bet_to_call:.2f}",
                        f"• Current pot size: ${pot_size:.2f}",
                        f"• Total pot if you call: ${pot_size:.2f} + ${bet_to_call:.2f} = ${total_pot:.2f}",
                        "",
                        "**Step 2: Calculate Pot Odds**",
                        f"• Pot odds formula: Total pot after call / Amount to call",
                        f"• Pot odds: ${total_pot:.2f} / ${bet_to_call:.2f} = {pot_odds_ratio:.2f}:1",
                        f"• Interpretation: You're getting {pot_odds_ratio:.2f}:1 on your money",
                        "",
                        "**Step 3: Calculate Required Equity**",
                        f"• Required equity formula: Call amount / Total pot after call",
                        f"• Required equity: ${bet_to_call:.2f} / ${total_pot:.2f} = {required_equity:.1f}%",
                        f"• Interpretation: You need to win at least {required_equity:.1f}% of the time to break even"
                    ]
                else:
                    result_parts = [
                        "Pot Odds & EV Analysis:",
                        f"• Call amount: ${bet_to_call:.2f}",
                        f"• Current pot: ${pot_size:.2f}",
                        f"• Total pot after call: ${total_pot:.2f}",
                        f"• Pot odds: {pot_odds_ratio:.2f}:1",
                        f"• Required equity to break even: {required_equity:.1f}%"
                    ]

                # Calculate EV if equity is provided
                if equity is not None:
                    # EV = (Probability of winning × Total pot) - Bet to call
                    equity_decimal = equity / 100
                    ev = (equity_decimal * total_pot) - bet_to_call

                    if teaching_mode:
                        result_parts.append("")
                        result_parts.append(f"**Step 4: Calculate Expected Value (EV) with {equity:.1f}% Equity**")
                        result_parts.append(f"• EV formula: (Win probability × Total pot) - Cost to call")
                        result_parts.append(f"• Win probability: {equity:.1f}% = {equity_decimal:.3f}")
                        result_parts.append(f"• EV = ({equity_decimal:.3f} × ${total_pot:.2f}) - ${bet_to_call:.2f}")
                        result_parts.append(f"• EV = ${equity_decimal * total_pot:.2f} - ${bet_to_call:.2f}")
                        result_parts.append(f"• **EV = ${ev:+.2f}**")
                        result_parts.append("")
                        result_parts.append("**Step 5: Make the Decision**")
                    else:
                        result_parts.append("")
                        result_parts.append(f"Expected Value (EV) with {equity:.1f}% equity:")
                        result_parts.append(f"• EV = ${ev:+.2f}")

                    if ev > 0:
                        if teaching_mode:
                            result_parts.append(f"• EV is POSITIVE (+${ev:.2f}) → This is a PROFITABLE call!")
                            result_parts.append(f"• Your equity ({equity:.1f}%) > Required equity ({required_equity:.1f}%)")
                            result_parts.append(f"• You'll win this hand {equity:.1f}% of the time")
                            roi = (ev / bet_to_call) * 100
                            result_parts.append(f"• Return on Investment (ROI): {roi:+.1f}%")
                            result_parts.append(f"• **Recommendation: CALL** ✅")
                            result_parts.append("")
                            result_parts.append("📚 **Teaching Note:**")
                            result_parts.append("   Even if you lose this specific hand, calling is the right decision long-term.")
                            result_parts.append(f"   Over many hands, you'll profit ${ev:.2f} on average per call.")
                        else:
                            result_parts.append(f"• Decision: ✅ PROFITABLE CALL (+EV)")
                            result_parts.append(f"• You have {equity:.1f}% equity vs {required_equity:.1f}% required")
                            roi = (ev / bet_to_call) * 100
                            result_parts.append(f"• ROI: {roi:+.1f}% on your ${bet_to_call:.2f} investment")
                    elif ev == 0:
                        result_parts.append(f"• Decision: ⚖️  BREAK-EVEN CALL (0 EV)")
                        result_parts.append(f"• You have exactly the required equity")
                    else:
                        if teaching_mode:
                            result_parts.append(f"• EV is NEGATIVE (-${abs(ev):.2f}) → This is an UNPROFITABLE call")
                            result_parts.append(f"• Your equity ({equity:.1f}%) < Required equity ({required_equity:.1f}%)")
                            result_parts.append(f"• You need {required_equity - equity:.1f}% more equity to justify calling")
                            result_parts.append(f"• **Recommendation: FOLD** ❌")
                            result_parts.append("")
                            result_parts.append("📚 **Teaching Note:**")
                            result_parts.append("   Even if you might win this hand, calling loses money long-term.")
                            result_parts.append(f"   Over many hands, you'll lose ${abs(ev):.2f} on average per call.")
                        else:
                            result_parts.append(f"• Decision: ❌ UNPROFITABLE CALL (-EV)")
                            result_parts.append(f"• You have {equity:.1f}% equity vs {required_equity:.1f}% required")
                            result_parts.append(f"• Expected loss: ${abs(ev):.2f} per call")
                else:
                    if teaching_mode:
                        result_parts.append("")
                        result_parts.append("**Next Step: Determine Your Equity**")
                        result_parts.append(f"• You need at least {required_equity:.1f}% equity to make calling profitable")
                        result_parts.append(f"• Use calculate_outs tool to determine your equity")
                        result_parts.append(f"• Then compare: Your equity vs {required_equity:.1f}% required")
                        result_parts.append("")
                        result_parts.append("**Example:**")
                        result_parts.append("  If you have a flush draw (9 outs on flop):")
                        result_parts.append("  • 9 outs × 4 = 36% equity")
                        result_parts.append(f"  • 36% > {required_equity:.1f}% required → Profitable call!")
                    else:
                        result_parts.append("")
                        result_parts.append(f"Interpretation: You need at least {required_equity:.1f}% equity to make calling profitable.")
                        result_parts.append(f"Tip: Add your equity as 3rd parameter (e.g., '{pot_size:.0f},{bet_to_call:.0f},35') for EV calculation.")

                return '\n'.join(result_parts)

            except ValueError:
                return "Invalid input: pot size, bet, and equity must be numbers"
            except Exception as e:
                logger.error(f"Error calculating pot odds/EV: {e}")
                return f"Calculation failed: {str(e)}"

        @tool
        def estimate_hand_strength(hand_description: str) -> str:
            """Estimate the strength of a poker hand with equity calculations and combinatorics.

            Input: Hand description (e.g., 'pocket aces', 'AKs', 'suited connectors', 'QQ')

            Provides:
            - Hand strength tier (premium/strong/medium/weak)
            - Approximate equity vs random hand preflop
            - Number of combinations for the hand
            - Probability of being dealt the hand
            - Strategic recommendations
            - Teaching explanation of why hand is strong/weak

            Use when teaching hand selection, evaluating preflop strength, or explaining probability.
            """
            hand_lower = hand_description.lower().strip()

            # Premium hands with detailed equity
            if 'aa' in hand_lower or 'aces' in hand_lower or 'pocket aces' in hand_lower:
                return """🃏 **Hand Strength: POCKET ACES (PREMIUM)**

**Equity Analysis:**
• Equity vs random hand: ~85% (17:3 favorite)
• Equity vs any pocket pair: ~80%
• Equity vs AK (best non-pair): ~93%

**Combinatorics:**
• Combinations: 6 (C(4,2) = 6 ways to make AA)
• Probability: 6/1326 = 0.45% chance (220:1 against)
• You'll be dealt AA once every 221 hands

**Strategic Recommendations:**
• Position: Extremely strong from ANY position
• Pre-flop: Raise/3-bet aggressively for value
• Goal: Build pot and isolate opponents
• Post-flop: Continue aggression but be aware of sets/straights

**Why it's Premium:**
• Highest starting hand in poker
• Dominates all other hands pre-flop
• Profitable to play in all situations

**Risk Awareness:**
• Vulnerable to sets on coordinated boards
• Can lose to straights/flushes
• Still only ~85% to win vs random - can lose 15% of the time"""

            elif 'kk' in hand_lower or 'kings' in hand_lower or 'pocket kings' in hand_lower:
                return """🃏 **Hand Strength: POCKET KINGS (PREMIUM)**

**Equity Analysis:**
• Equity vs random hand: ~82% (11:2 favorite)
• Equity vs any pocket pair (except AA): ~80%
• Equity vs AA: ~18% (dominated)

**Combinatorics:**
• Combinations: 6
• Probability: 0.45% chance (220:1 against)
• Same frequency as any pocket pair

**Strategic Recommendations:**
• Position: Very strong from any position
• Pre-flop: Raise/3-bet aggressively
• Goal: Build pot, watch for aces on board
• Vs heavy resistance: Consider opponent might have AA

**Why it's Premium:**
• Second-best starting hand
• Wins against almost all hands
• Only significantly behind AA pre-flop

**Risk Awareness:**
• Dominated by AA (18% equity)
• Vulnerable to aces on the flop
• Set mining opponents dangerous"""

            elif 'qq' in hand_lower or 'queens' in hand_lower or 'pocket queens' in hand_lower:
                return """🃏 **Hand Strength: POCKET QUEENS (PREMIUM)**

**Equity Analysis:**
• Equity vs random hand: ~80%
• Equity vs AA: ~18%, vs KK: ~18%
• Equity vs AK: ~54% (slight favorite)

**Combinatorics:**
• Combinations: 6
• Probability: 0.45%
• Third-most premium pocket pair

**Strategic Recommendations:**
• Position: Strong from any position
• Pre-flop: Raise, consider re-raise
• Be cautious if A or K hits the flop
• Watch for multiple opponents (increases chance of overcards)

**Why it's Premium:**
• Third-best starting hand
• Strong equity against most hands
• Can win unimproved

**Risk Awareness:**
• Behind AA, KK (only ~18% equity vs either)
• Overcards (A, K) on board are dangerous
• Difficult to play vs heavy resistance"""

            elif 'jj' in hand_lower or 'pocket jacks' in hand_lower:
                return """🃏 **Hand Strength: POCKET JACKS (STRONG)**

**Equity Analysis:**
• Equity vs random hand: ~77%
• Equity vs AA/KK/QQ: ~18% (dominated)
• Equity vs AK: ~57% (small favorite)

**Combinatorics:**
• Combinations: 6
• Probability: 0.45%

**Strategic Recommendations:**
• Position: Strong, but position-dependent strength
• Pre-flop: Raise from most positions
• Post-flop: Careful of overcards (A, K, Q)
• Fold to heavy resistance from tight players

**Why it's Strong:**
• Still a very good hand (wins 77% vs random)
• Profitable from all positions
• Top 5 starting hand

**Risk Awareness:**
• Behind QQ+, dominated by higher pairs
• 3 overcard ranks (A, K, Q) make post-flop tricky
• Difficult hand to play for beginners"""

            elif 'aks' in hand_lower or 'a♠k♠' in hand_lower or 'a♥k♥' in hand_lower or 'a♦k♦' in hand_lower or 'a♣k♣' in hand_lower or ('ak' in hand_lower and 'suited' in hand_lower):
                return """🃏 **Hand Strength: ACE-KING SUITED (STRONG)**

**Equity Analysis:**
• Equity vs random hand: ~67%
• Equity vs AA: ~12%, vs KK: ~30%, vs QQ: ~47%
• Equity vs AKo: ~58% (slightly better)

**Combinatorics:**
• Combinations: 4 (one per suit)
• Probability: 4/1326 = 0.30% (331:1 against)
• Much rarer than AKo (12 combos)

**Draw Potential:**
• Can make: Top pair, flush, straight, two pair
• Flush draw: 9 outs when you have flush draw
• Straight draw: Potential broadway straight (TJQKA)

**Strategic Recommendations:**
• Position: Strong from any position
• Pre-flop: Raise/3-bet for value
• Post-flop: Strong with top pair, powerful draws
• Can barrel on many boards

**Why it's Strong:**
• Big cards: makes top pair top kicker
• Flush potential: adds 4-9% equity
• Straight potential: Broadway draws
• Blocks AA and KK (removes some combinations)

**Risk Awareness:**
• Only Ace-high if you miss (loses to any pair)
• Behind all pocket pairs pre-flop
• Needs to improve to win at showdown"""

            elif ('ak' in hand_lower and 'offsuit' in hand_lower) or 'ako' in hand_lower:
                return """🃏 **Hand Strength: ACE-KING OFFSUIT (STRONG)**

**Equity Analysis:**
• Equity vs random hand: ~65%
• Equity vs AA: ~7%, vs KK: ~29%, vs QQ: ~43%
• Equity vs AKs: ~42%

**Combinatorics:**
• Combinations: 12 (4 aces × 3 kings each = 12)
• Probability: 12/1326 = 0.90% (110:1 against)
• 3× more common than AKs

**Strategic Recommendations:**
• Position: Strong from any position
• Pre-flop: Raise, consider 3-betting
• Post-flop: Play aggressively with top pair
• Can represent strength on many boards

**Why it's Strong:**
• Makes top pair top kicker
• Blocks premium hands (AA, KK)
• High card strength
• Can make broadway straight

**Risk Awareness:**
• Only Ace-high if miss completely
• No flush potential
• Behind all pocket pairs pre-flop
• Needs to hit to win"""

            elif any(strong in hand_lower for strong in ['99', 'tt', '10-10', 'tens', 'nines']):
                return """🃏 **Hand Strength: MEDIUM POCKET PAIR (TT/99)**

**Equity Analysis:**
• Equity vs random hand: ~70-73%
• Equity vs AA/KK/QQ/JJ: ~18%
• Equity vs overcards (AK, AQ): ~52-55% (slight favorite)

**Combinatorics:**
• Combinations: 6 per rank
• Probability: 0.45%

**Strategic Recommendations:**
• Position: Playable from all positions, strength increases late
• Pre-flop: Raise from most positions
• Set mining: Call to see flop and hit set (11.8% chance)
• Fold to extreme pressure from tight opponents

**Why it's Medium:**
• Decent equity vs most hands
• Can win unimproved
• Set mining potential (very strong when you hit)

**Risk Awareness:**
• Many overcards on most flops
• Behind higher pairs
• Tricky to play when overcards appear"""

            elif 'suited connector' in hand_lower or any(x in hand_lower for x in ['jts', 't9s', '98s', '87s']):
                return """🃏 **Hand Strength: SUITED CONNECTORS (MEDIUM/SPECULATIVE)**

**Equity Analysis:**
• Equity vs random hand: ~55-63% (depends on specific hand)
• Equity vs AA: ~20-23%
• Equity vs AK: ~40-45%

**Combinatorics:**
• Each specific suited connector: 4 combinations
• All suited connectors (JTs-32s): 48 combinations
• Probability (specific): 0.30%

**Draw Potential:**
• Straight possibilities: Open-ended (8 outs), gutshot (4 outs)
• Flush possibilities: 9 outs when you flop flush draw
• Can make strong hidden hands (straights, flushes)

**Strategic Recommendations:**
• Position: POSITION-DEPENDENT (play from late position)
• Pre-flop: Usually call/limp, occasionally raise from late
• Post-flop: Strong with draws, can semi-bluff
• Implied odds: Need good pot odds to play profitably

**Why it's Medium/Speculative:**
• Rarely best hand currently
• Powerful when you hit draws
• Deceptive (opponents don't expect big hands)
• Playability (many ways to improve)

**Risk Awareness:**
• Usually behind pre-flop
• Needs to improve to win
• Expensive if you miss draws
• Better with deep stacks (implied odds)

**Probability Teaching:**
• Flopping flush draw: ~11%
• Flopping open-ended straight draw: ~9-10%
• Making flush by river (when flopped): ~35%
• Making straight by river (when flopped OESD): ~32%"""

            elif any(small in hand_lower for small in ['22', '33', '44', '55', '66', 'low pair', 'small pair']):
                return """🃏 **Hand Strength: SMALL POCKET PAIRS (22-66)**

**Equity Analysis:**
• Equity vs random hand: ~50-60% (increases with higher pair)
• Equity vs overcards (AK, AQ, etc.): ~52-54% (slight favorite)
• Equity vs higher pairs: ~18%

**Combinatorics:**
• Combinations: 6 per specific pair
• Probability: 0.45% per specific pair

**Set Mining Strategy:**
• Flop a set: 11.8% chance (~7.5:1 against)
• Set vs overpair: ~80-90% equity (huge reversal)
• Need 10:1 implied odds to call pre-flop profitably

**Strategic Recommendations:**
• Position: Mostly late position, fold early vs raises
• Pre-flop: Set mine (call to hit set), fold vs re-raises
• Post-flop: Usually fold if you don't hit set
• Pot odds: Need ~10:1 implied to call pre-flop raise

**Why it's Weak/Speculative:**
• Almost always faces overcards on the flop
• Rarely best hand if you don't improve
• Profitable only with deep stacks (implied odds)
• Easy to fold when you miss

**Probability Teaching:**
• Chance to flop set: ~11.8% (1 in 8.5 flops)
• Need to win 10× your call when you hit set
• Example: Call $10 to win $100+ when you flop set

**Risk Awareness:**
• Very vulnerable to overcards
• Difficult to play for stacks
• Profitable only with good implied odds"""

            else:
                return """🃏 **Hand Strength: UNABLE TO CLASSIFY**

Unable to categorize this hand. Please provide more specific details:

**Specific Hands:**
• Pocket pairs: 'AA', 'KK', 'QQ', 'JJ', 'TT', '99', etc.
• Suited: 'AKs', 'KQs', 'JTs', 'T9s'
• Offsuit: 'AKo', 'KQo'
• Both: 'AK', 'KQ'

**Hand Categories:**
• 'suited connectors'
• 'pocket pairs'
• 'broadway cards'

**For Post-Flop Analysis:**
• Include board cards: e.g., "QQ on K82 flop"
• Use count_combinations tool for specific combo counts
• Use calculate_outs tool for draw equity"""

        @tool
        def calculate_outs(hand_situation: str) -> str:
            """Calculate outs, equity, and probability for poker situations.

            Essential for teaching poker probability fundamentals.

            Input formats:
            1. 'cards,board,draw_type' - e.g., 'A♠K♠,Q♠9♠2♣,flush' or 'JT,Q98,straight'
            2. Simple description - e.g., 'flush draw on flop', 'gutshot straight draw'

            Common draw types:
            - flush: 9 outs
            - oesd/open-ended: 8 outs (open-ended straight draw)
            - gutshot: 4 outs (inside straight draw)
            - pair: 2 outs (hitting set with pocket pair)
            - overcards: 6 outs (two overcards)

            Returns:
            - Number of outs
            - Equity percentage using Rule of 2 and 4
            - Exact probability calculations
            - Teaching explanation of the math

            Use when teaching outs, equity, or probability concepts.
            """
            try:
                situation_lower = hand_situation.lower()

                # Determine outs based on draw type
                outs = 0
                draw_type = ""
                explanation_parts = []

                # Parse draw type from input
                if 'flush' in situation_lower:
                    outs = 9
                    draw_type = "Flush draw"
                    explanation_parts.append("• Flush draw: 9 remaining cards of your suit")
                    explanation_parts.append("  (13 cards per suit - 4 already visible = 9 outs)")

                elif 'oesd' in situation_lower or 'open-ended' in situation_lower or 'open ended' in situation_lower:
                    outs = 8
                    draw_type = "Open-ended straight draw"
                    explanation_parts.append("• Open-ended straight draw: 8 outs")
                    explanation_parts.append("  (4 cards on high end + 4 cards on low end = 8 outs)")

                elif 'gutshot' in situation_lower or 'inside' in situation_lower:
                    outs = 4
                    draw_type = "Gutshot straight draw"
                    explanation_parts.append("• Gutshot (inside) straight draw: 4 outs")
                    explanation_parts.append("  (Only 1 rank completes straight, 4 suits = 4 outs)")

                elif 'pair' in situation_lower and ('set' in situation_lower or 'trips' in situation_lower):
                    outs = 2
                    draw_type = "Pocket pair to set"
                    explanation_parts.append("• Pocket pair improving to set: 2 outs")
                    explanation_parts.append("  (2 remaining cards of your rank)")

                elif 'overcard' in situation_lower:
                    outs = 6
                    draw_type = "Two overcards"
                    explanation_parts.append("• Two overcards: 6 outs")
                    explanation_parts.append("  (3 cards for each overcard rank = 6 outs)")

                elif 'combo' in situation_lower or 'flush+straight' in situation_lower:
                    outs = 15
                    draw_type = "Combo draw (flush + straight)"
                    explanation_parts.append("• Flush draw: 9 outs")
                    explanation_parts.append("• Straight draw: 8 outs")
                    explanation_parts.append("• Overlap: -2 outs (cards counted twice)")
                    explanation_parts.append("• Total: 9 + 8 - 2 = 15 outs")

                else:
                    # Try to extract number from input
                    import re
                    numbers = re.findall(r'\b(\d+)\s*out', situation_lower)
                    if numbers:
                        outs = int(numbers[0])
                        draw_type = f"{outs}-out draw"
                        explanation_parts.append(f"• {draw_type} specified")
                    else:
                        return """Unable to determine draw type. Please specify:
- 'flush draw' (9 outs)
- 'open-ended straight' or 'oesd' (8 outs)
- 'gutshot' (4 outs)
- 'two overcards' (6 outs)
- 'pair to set' (2 outs)
- Or use format: 'A♠K♠,Q♠9♠2♣,flush'"""

                if outs == 0:
                    return "No outs calculated. Please specify draw type."

                # Calculate on different streets
                on_turn = 'turn' in situation_lower
                on_river = 'river' in situation_lower
                on_flop = not on_turn and not on_river  # Default to flop

                result_parts = [
                    f"📊 OUTS & EQUITY CALCULATION: {draw_type}",
                    "",
                    "Outs Identified:",
                    *explanation_parts,
                    f"• **Total Outs: {outs}**",
                    ""
                ]

                # Rule of 2 and 4 calculations
                if on_flop:
                    equity_rule_of_4 = min(outs * 4, 100)  # Cap at 100%
                    unseen_cards = 52 - 5  # 47 unseen cards on flop

                    result_parts.extend([
                        "Equity Calculation (on Flop with 2 cards to come):",
                        f"• **Rule of 4: {outs} outs × 4 ≈ {equity_rule_of_4}% equity**",
                        "",
                        "Exact Probability Breakdown:",
                        f"• Chance to hit on turn: {outs}/{unseen_cards} = {(outs/unseen_cards)*100:.1f}%",
                        f"• If miss turn, chance on river: {outs}/{unseen_cards-1} = {(outs/(unseen_cards-1))*100:.1f}%",
                        f"• Combined probability to hit by river: ~{min(equity_rule_of_4, 100):.0f}%",
                        "",
                        f"💡 **Interpretation**: You will complete your {draw_type.lower()} about {equity_rule_of_4}% of the time (roughly {100//equity_rule_of_4 if equity_rule_of_4 > 0 else '?'} to 1 against)"
                    ])

                elif on_turn:
                    equity_rule_of_2 = min(outs * 2, 100)
                    unseen_cards = 52 - 6  # 46 unseen cards on turn

                    result_parts.extend([
                        "Equity Calculation (on Turn with 1 card to come):",
                        f"• **Rule of 2: {outs} outs × 2 ≈ {equity_rule_of_2}% equity**",
                        "",
                        "Exact Probability:",
                        f"• Chance to hit on river: {outs}/{unseen_cards} = {(outs/unseen_cards)*100:.1f}%",
                        "",
                        f"💡 **Interpretation**: You will complete your {draw_type.lower()} about {equity_rule_of_2}% of the time (roughly {100//equity_rule_of_2 if equity_rule_of_2 > 0 else '?'} to 1 against)"
                    ])

                else:  # river
                    result_parts.append("⚠️ On river: No more cards to come, outs calculation not applicable")
                    result_parts.append("You either made your hand or you didn't!")

                # Add teaching notes
                if on_flop:
                    result_parts.extend([
                        "",
                        "📚 **Teaching Note: Rule of 2 and 4**",
                        "• On FLOP (2 cards to come): Multiply outs by 4 for approximate equity",
                        "• On TURN (1 card to come): Multiply outs by 2 for approximate equity",
                        "• This is a quick mental shortcut for calculating equity at the table",
                        "",
                        "**Example Use**: If pot odds require 25% equity and you have 7 outs:",
                        "  7 × 4 = 28% equity > 25% required → Profitable call!"
                    ])

                return '\n'.join(result_parts)

            except Exception as e:
                logger.error(f"Error calculating outs: {e}")
                return f"Error calculating outs: {str(e)}. Use format like 'flush draw on flop' or 'A♠K♠,Q♠9♠2♣,flush'"

        @tool
        def count_combinations(hand_description: str) -> str:
            """Count poker hand combinations for probability and range analysis.

            Essential for teaching poker combinatorics and probability fundamentals.

            Input: Hand description
            - Specific hands: 'AA', 'AK', 'KQs', 'JTo'
            - Hand categories: 'pocket pairs', 'suited connectors', 'broadway cards'

            Returns:
            - Number of combinations for that hand/category
            - Probability of being dealt that hand
            - Teaching explanation of the combinatorics

            Use when teaching probability, ranges, or how to count hand combinations.
            """
            try:
                hand_lower = hand_description.lower().strip()

                # Remove common words
                hand_lower = hand_lower.replace('suited', 's').replace('offsuit', 'o')

                combos = 0
                prob_percent = 0
                explanation = []
                total_hands = 1326  # C(52, 2) = 1,326 total starting hands

                # Specific pocket pairs (AA, KK, QQ, etc.)
                if len(hand_lower) == 2 and hand_lower[0] == hand_lower[1]:
                    combos = 6
                    hand_rank = hand_lower[0].upper()
                    explanation = [
                        f"**Pocket Pair ({hand_rank}{hand_rank}): 6 combinations**",
                        "",
                        "Combinatorics:",
                        f"• Number of {hand_rank} cards in deck: 4",
                        "• Ways to choose 2 from 4: C(4,2) = 6",
                        "",
                        "All 6 combinations:",
                        f"• {hand_rank}♠{hand_rank}♥, {hand_rank}♠{hand_rank}♦, {hand_rank}♠{hand_rank}♣",
                        f"• {hand_rank}♥{hand_rank}♦, {hand_rank}♥{hand_rank}♣, {hand_rank}♦{hand_rank}♣"
                    ]

                # Suited hands (AKs, KQs, etc.)
                elif 's' in hand_lower and len(hand_lower.replace('s', '')) == 2:
                    combos = 4
                    cards = hand_lower.replace('s', '').upper()
                    explanation = [
                        f"**Suited Hand ({cards}s): 4 combinations**",
                        "",
                        "Combinatorics:",
                        "• Must match suits: both spades, both hearts, both diamonds, or both clubs",
                        "• Number of suits: 4",
                        "",
                        "All 4 combinations:",
                        f"• {cards[0]}♠{cards[1]}♠ (spades)",
                        f"• {cards[0]}♥{cards[1]}♥ (hearts)",
                        f"• {cards[0]}♦{cards[1]}♦ (diamonds)",
                        f"• {cards[0]}♣{cards[1]}♣ (clubs)"
                    ]

                # Offsuit hands (AKo, KQo, etc.)
                elif 'o' in hand_lower and len(hand_lower.replace('o', '')) == 2:
                    combos = 12
                    cards = hand_lower.replace('o', '').upper()
                    explanation = [
                        f"**Offsuit Hand ({cards}o): 12 combinations**",
                        "",
                        "Combinatorics:",
                        f"• Number of {cards[0]} cards: 4",
                        f"• Number of {cards[1]} cards: 4",
                        "• Total combinations: 4 × 4 = 16",
                        "• Minus suited combos: 16 - 4 = 12 offsuit",
                        "",
                        "Examples of offsuit combinations:",
                        f"• {cards[0]}♠{cards[1]}♥, {cards[0]}♠{cards[1]}♦, {cards[0]}♠{cards[1]}♣",
                        f"• {cards[0]}♥{cards[1]}♠, {cards[0]}♥{cards[1]}♦, {cards[0]}♥{cards[1]}♣",
                        "• ... (12 total)"
                    ]

                # Unpaired hands (AK, KQ, etc.) - both suited and offsuit
                elif len(hand_lower) == 2 and hand_lower[0] != hand_lower[1]:
                    combos = 16
                    cards = hand_lower.upper()
                    explanation = [
                        f"**All {cards} Hands (suited + offsuit): 16 combinations**",
                        "",
                        "Breakdown:",
                        f"• Suited ({cards}s): 4 combos",
                        f"• Offsuit ({cards}o): 12 combos",
                        "• **Total: 16 combos**",
                        "",
                        "Combinatorics:",
                        f"• {cards[0]} cards in deck: 4",
                        f"• {cards[1]} cards in deck: 4",
                        "• Total combinations: 4 × 4 = 16"
                    ]

                # Hand categories
                elif 'pocket pair' in hand_lower:
                    combos = 78
                    explanation = [
                        "**All Pocket Pairs: 78 combinations**",
                        "",
                        "Breakdown:",
                        "• 13 ranks (22, 33, 44, ..., AA)",
                        "• Each pocket pair has 6 combos",
                        "• Total: 13 × 6 = 78 combinations",
                        "",
                        "Individual pocket pairs:",
                        "• AA: 6 combos, KK: 6 combos, QQ: 6 combos",
                        "• JJ: 6 combos, TT: 6 combos, ..., 22: 6 combos"
                    ]

                elif 'suited connector' in hand_lower:
                    combos = 48
                    explanation = [
                        "**All Suited Connectors: 48 combinations**",
                        "",
                        "Suited connectors: JTs, T9s, 98s, 87s, 76s, 65s, 54s, 43s, 32s, AKs, KQs, QJs",
                        "• 12 different suited connector hands",
                        "• Each has 4 combos (one per suit)",
                        "• Total: 12 × 4 = 48 combinations"
                    ]

                elif 'broadway' in hand_lower:
                    combos = 150
                    explanation = [
                        "**All Broadway Hands (A,K,Q,J,T): 150 combinations**",
                        "",
                        "Broadway ranks: A, K, Q, J, T (10)",
                        "• Total broadway cards: 5 ranks × 4 suits = 20 cards",
                        "• Combinations of 2 cards from 20: C(20,2) = 190",
                        "• But we only count unpaired: 190 - 40 pairs = 150",
                        "",
                        "Examples: AA, KK, QQ, JJ, TT, AK, AQ, AJ, AT, KQ, KJ, KT, QJ, QT, JT"
                    ]

                else:
                    return """Unable to parse hand description. Please use:

**Specific Hands:**
• Pocket pairs: 'AA', 'KK', 'QQ'
• Suited: 'AKs', 'KQs', 'JTs'
• Offsuit: 'AKo', 'KQo', 'JTo'
• Both: 'AK', 'KQ', 'JT'

**Categories:**
• 'pocket pairs' (all pairs)
• 'suited connectors'
• 'broadway hands' (A,K,Q,J,T)"""

                # Calculate probability
                if combos > 0:
                    prob_percent = (combos / total_hands) * 100
                    odds_against = (total_hands / combos) - 1 if combos > 0 else 0

                    result = '\n'.join(explanation)
                    result += f"\n\n📊 **Probability**:"
                    result += f"\n• Combinations: {combos} out of {total_hands} total hands"
                    result += f"\n• Probability: {combos}/{total_hands} = {prob_percent:.2f}%"
                    result += f"\n• Odds: ~{odds_against:.1f}:1 against being dealt this hand"

                    # Add teaching note
                    result += "\n\n📚 **Teaching Note**: Understanding combinations is key to range analysis."
                    result += "\n   Knowing how many combos exist helps estimate opponent ranges and equity calculations."

                    return result
                else:
                    return "Could not calculate combinations."

            except Exception as e:
                logger.error(f"Error counting combinations: {e}")
                return f"Error: {str(e)}"

        @tool
        def analyze_position(position_info: str) -> str:
            """Analyze poker position advantage/disadvantage. Input: Position name (e.g., 'button', 'small blind', 'early position'). Provides position strength assessment, advantages/disadvantages, strategic recommendations, and hand range suggestions. Use when discussing position-based strategy or when position affects the decision."""
            position_lower = position_info.lower()

            # Button (best position)
            if 'button' in position_lower or 'btn' in position_lower:
                return """Position: BUTTON (Best Position)

Advantages:
• Last to act post-flop (maximum information)
• Can steal blinds with wider range
• Control pot size and betting
• See all opponents act before you

Strategy:
• Raise 40-50% of hands
• Play aggressively
• Steal blinds frequently
• Exploit tight players

This is the most profitable position in poker!"""

            # Cutoff (second best)
            if 'cutoff' in position_lower or 'co' in position_lower:
                return """Position: CUTOFF (Strong Position)

Advantages:
• Second-best position
• Only button acts after you post-flop
• Good stealing position
• Can isolate button

Strategy:
• Raise 35-45% of hands
• Steal blinds when button folds
• Re-raise tight players
• Play strong draws aggressively"""

            # Small Blind
            if 'small blind' in position_lower or 'sb' in position_lower:
                return """Position: SMALL BLIND (Difficult Position)

Disadvantages:
• Second to act post-flop (out of position)
• Already invested half blind
• Hard to defend profitably
• Big blind acts after you

Strategy:
• Tight range (top 15-20% of hands)
• Consider pot odds with decent hands
• Fold marginal hands
• Don't defend too wide just because you invested SB"""

            # Big Blind
            if 'big blind' in position_lower or 'bb' in position_lower:
                return """Position: BIG BLIND (Defensive Position)

Characteristics:
• Last to act pre-flop
• Already invested full blind
• Out of position post-flop
• Must defend vs steals

Strategy:
• Defend vs late position raises (pot odds)
• Can check pre-flop if no raise
• 3-bet vs obvious steals
• Play tighter vs early position raises"""

            # Early Position
            if any(ep in position_lower for ep in ['early', 'utg', 'under the gun', 'ep']):
                return """Position: EARLY POSITION (Weakest Position)

Disadvantages:
• Most players act after you
• Minimal information
• Hard to play speculative hands
• Easy to get trapped

Strategy:
• Very tight range (top 10-15% hands)
• Premium hands only
• Avoid marginal hands
• Don't bluff often"""

            # Middle Position
            if 'middle' in position_lower or 'mp' in position_lower:
                return """Position: MIDDLE POSITION (Neutral Position)

Characteristics:
• Some players behind, some folded
• Moderate information
• Balanced strategy needed

Strategy:
• Play top 20-25% of hands
• Tighter than late position
• Looser than early position
• Adjust based on table dynamics"""

            return """Position Analysis: UNKNOWN

Please specify position:
- Button/BTN (best)
- Cutoff/CO (strong)
- Middle Position/MP (neutral)
- Early Position/UTG/EP (weak)
- Small Blind/SB (difficult)
- Big Blind/BB (defensive)"""

        @tool
        def get_recent_hands(limit: str = "3") -> str:
            """Get PAST/HISTORICAL poker hands (NOT the current active hand).

            ⚠️ CRITICAL: This tool is for COMPLETED hands from history ONLY!
            ❌ DO NOT use for questions about the CURRENT/ACTIVE hand
            ❌ DO NOT use when user asks "what is my current hand" or "my hand"
            ✅ The current hand is ALWAYS in the [CURRENT GAME STATE] block (auto-provided)

            This tool shows PAST hands in chronological order (newest first):
            - Completed hands from previous rounds
            - Historical performance data
            - Session progression over time

            Input: limit - Number of PAST hands to retrieve (default: 3, max: 10)
            Returns: HISTORICAL hands with their cards, board, outcome, and profit/loss

            Use ONLY for these types of questions:
            - "What happened in my LAST hand?" (the hand that just finished)
            - "Show me my RECENT hands" (past completed hands)
            - "How have I been doing LATELY?" (historical performance)

            DO NOT use for:
            - "What is my CURRENT hand?" → Read [CURRENT GAME STATE] block instead!
            - "Should I call THIS hand?" → Read [CURRENT GAME STATE] block instead!
            """
            if not hand_history:
                return "Hand history not available. This feature requires hand history tracking to be enabled."

            try:
                # Parse limit
                try:
                    limit_int = int(limit)
                    limit_int = min(max(1, limit_int), 10)  # Clamp between 1 and 10
                except:
                    limit_int = 3

                logger.info(f"📅 Getting {limit_int} most recent hands (by timestamp)")

                # Get recent hands sorted by timestamp
                results = hand_history.get_recent_hands(limit=limit_int)

                if not results:
                    logger.info("No recent hands found")
                    return "No hands found in your history yet. Start playing to build your history!"

                logger.info(f"Found {len(results)} recent hands")

                # Format results for LLM
                response_parts = [
                    f"📅 RECENT HANDS (sorted by time, newest first)",
                    f"Showing your last {len(results)} hands:\n"
                ]

                for i, hand in enumerate(results, 1):
                    your_cards = hand.get('your_cards', [])
                    board = hand.get('board', [])
                    outcome = hand.get('outcome', 'unknown')
                    profit = hand.get('profit', 0)
                    pot = hand.get('pot', 0)
                    position = hand.get('position', 'unknown')
                    timestamp = hand.get('timestamp', 'unknown')
                    hand_id = hand.get('hand_id', 'unknown')

                    # Format hand details
                    cards_str = ', '.join(your_cards) if your_cards else 'Unknown'
                    board_str = ', '.join(board) if board else 'No board'

                    # Show relative time (newest = #1)
                    response_parts.append(f"\n{i}. [RECENT] Hand from: {timestamp}")
                    response_parts.append(f"   Hand ID: {hand_id}")
                    response_parts.append(f"   Your cards: {cards_str}")
                    response_parts.append(f"   Board: {board_str}")
                    response_parts.append(f"   Position: {position}")
                    response_parts.append(f"   Pot: ${pot} | Outcome: {outcome} | Profit: ${profit:+d}")

                return '\n'.join(response_parts)

            except Exception as e:
                logger.error(f"Error getting recent hands: {e}")
                import traceback
                traceback.print_exc()
                return f"Could not get recent hands: {str(e)}"

        # Core tools (ordered by importance)
        tools = [
            search_poker_knowledge,      # RAG for strategy
            calculate_pot_odds,           # Math for decisions
            calculate_outs,               # Equity calculation
            count_combinations,           # Probability teaching
            estimate_hand_strength,       # Hand evaluation
            analyze_position,             # Position strategy
            get_recent_hands,             # Hand history
            get_game_state,               # DEPRECATED - state is auto-injected now
        ]

        return tools
