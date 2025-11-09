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

    def __init__(self, pinecone_store, game_context_provider=None, decision_tracker=None):
        """
        Initialize poker tools

        Args:
            pinecone_store: PineconePokerStore instance for RAG
            game_context_provider: GameContextProvider for current game state
            decision_tracker: DecisionTracker instance for decision history (optional)
        """
        self.pinecone_store = pinecone_store
        self.game_context_provider = game_context_provider
        self.decision_tracker = decision_tracker

    def create_tools(self) -> List:
        """
        Create all poker tools for the agent using @tool decorator

        Returns:
            List of LangChain tool functions
        """
        # Create closures over self to access store, context provider, and decision tracker
        pinecone_store = self.pinecone_store
        game_context_provider = self.game_context_provider
        decision_tracker = self.decision_tracker

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
            """Get the current poker game state including player's hole cards, position at the table, current hand phase, board cards, pot size, and opponent information. Use this FIRST when providing situation-specific advice or recommendations."""
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
            """Calculate pot odds mathematically. Input format: 'pot_size,bet_to_call' (comma-separated numbers). Example: '150,30' means pot is $150 and you need to call $30. Use this when user asks 'should I call?' or wants to know pot odds. Always provide pot size and bet amount from the game state."""
            try:
                # Parse input
                parts = input_str.strip().split(',')
                if len(parts) != 2:
                    return "Invalid input. Use format: pot_size,bet_to_call (e.g., '100,20')"

                pot_size = int(parts[0].strip())
                bet_to_call = int(parts[1].strip())

                if bet_to_call == 0:
                    return "No bet to call - you can check for free (no pot odds needed)"

                if pot_size < 0 or bet_to_call < 0:
                    return "Invalid input: pot size and bet must be positive numbers"

                # Calculate pot odds
                total_pot = pot_size + bet_to_call
                pot_odds_ratio = total_pot / bet_to_call
                pot_odds_percentage = (bet_to_call / total_pot) * 100
                required_equity = pot_odds_percentage

                result = f"""Pot Odds Analysis:
• Call amount: ${bet_to_call}
• Current pot: ${pot_size}
• Total pot after call: ${total_pot}
• Pot odds: {pot_odds_ratio:.2f}:1
• Required equity to break even: {required_equity:.1f}%

Interpretation: You need at least {required_equity:.1f}% chance of winning to make calling profitable."""

                return result

            except ValueError:
                return "Invalid input: pot size and bet must be numbers"
            except Exception as e:
                logger.error(f"Error calculating pot odds: {e}")
                return f"Pot odds calculation failed: {str(e)}"

        @tool
        def estimate_hand_strength(hand_description: str) -> str:
            """Estimate the strength of a poker hand. Input: Hand description (e.g., 'pocket aces', 'A♠ K♥', 'suited connectors'). Provides hand strength tier (premium, strong, medium, weak), win rate vs random hand, strategic recommendations, and position considerations. Use when evaluating whether to play a hand or assessing current hand quality."""
            hand_lower = hand_description.lower()

            # Premium hands
            if any(premium in hand_lower for premium in ['aa', 'aces', 'pocket aces', 'kk', 'kings', 'pocket kings', 'qq', 'queens']):
                return """Hand Strength: PREMIUM (Top tier)
- Win rate: 80-85% vs random hand pre-flop
- Strategy: Raise/re-raise aggressively
- Position: Strong from any position
- Risk: Vulnerable to sets and straights on certain boards"""

            # Strong hands
            if any(strong in hand_lower for strong in ['ak', 'aq', 'jj', 'pocket jacks', 'aj', '10-10', 'tt']):
                return """Hand Strength: STRONG (High tier)
- Win rate: 55-70% vs random hand pre-flop
- Strategy: Raise from most positions, consider re-raising
- Position: Playable from all positions
- Risk: Difficult to play post-flop if you don't improve"""

            # Medium hands
            if any(medium in hand_lower for medium in ['99', '88', '77', 'kq', 'kj', 'qt', 'a-10', 'suited']):
                return """Hand Strength: MEDIUM (Playable)
- Win rate: 45-60% vs random hand pre-flop
- Strategy: Raise from late position, call from early
- Position: Position-dependent
- Risk: Needs to improve or catch favorable flop"""

            # Weak hands
            if any(weak in hand_lower for weak in ['66', '55', '44', '33', '22', 'low', 'weak']):
                return """Hand Strength: WEAK (Speculative)
- Win rate: 30-45% vs random hand
- Strategy: Fold from early position, call from late position
- Position: Only play from late position with good odds
- Risk: High - needs very favorable flop"""

            return """Hand Strength: UNKNOWN
Unable to categorize this hand. Please provide more details like:
- Specific cards (e.g., "A♠ K♥")
- Hand type (e.g., "pocket aces", "suited connectors")
- Current board cards for post-flop analysis"""

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
        def search_past_decisions(situation_description: str) -> str:
            """Search your past poker decisions for similar situations. Input: Description of current situation (e.g., 'pocket jacks on button facing raise', 'top pair on flop with draw'). Returns: Similar past decisions with their outcomes and profitability. Use this to learn from your own playing history and see which actions worked best in similar spots."""
            if not decision_tracker:
                return "Decision history not available. This feature requires decision tracking to be enabled."

            try:
                # Search for similar pre-decisions
                results = decision_tracker.search_similar_decisions(
                    query=situation_description,
                    decision_type='pre_decision',
                    top_k=3
                )

                if not results:
                    return "No similar past decisions found in your history. This might be a new situation for you!"

                # Format results for LLM
                response_parts = [f"Found {len(results)} similar decisions from your past:\n"]

                for i, result in enumerate(results, 1):
                    metadata = result.get('metadata', {})
                    similarity = result.get('score', 0)

                    # Extract pre-decision info
                    your_cards = metadata.get('your_cards', [])
                    if isinstance(your_cards, str):
                        import json
                        try:
                            your_cards = json.loads(your_cards)
                        except:
                            your_cards = []

                    position = metadata.get('position', 'unknown')
                    pot = metadata.get('pot', 0)
                    to_call = metadata.get('chips_to_call', 0)

                    # Try to find corresponding post-decision
                    decision_id = metadata.get('decision_id', '')

                    # Format this decision
                    response_parts.append(f"\n{i}. Similarity: {similarity:.2f}")
                    response_parts.append(f"   Situation: {', '.join(your_cards)} in {position}")
                    response_parts.append(f"   Pot: ${pot}, To call: ${to_call}")

                    # Add description
                    description = metadata.get('description', '')
                    if description:
                        response_parts.append(f"   Context: {description[:150]}...")

                    # Note: Outcome info would be in post-decision record
                    # For now, indicate that we found the situation
                    response_parts.append(f"   (Check post-decision data for outcome)")

                return '\n'.join(response_parts)

            except Exception as e:
                logger.error(f"Error searching past decisions: {e}")
                return f"Could not search decision history: {str(e)}"

        tools = [
            search_poker_knowledge,
            get_game_state,
            calculate_pot_odds,
            estimate_hand_strength,
            analyze_position,
            search_past_decisions
        ]

        return tools


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Poker Tools Example Usage\n")
    print("="*60)

    # Mock stores for testing
    class MockPinecone:
        def search_as_context(self, query, k=2):
            return f"Mock knowledge: Strategy for '{query}'"

    class MockGameContext:
        def get_full_context(self):
            return "Mock game state: You have A♠ K♠ on the button"

    # Create tools
    tools_manager = PokerTools(
        pinecone_store=MockPinecone(),
        game_context_provider=MockGameContext()
    )

    tools = tools_manager.create_tools()

    print(f"Created {len(tools)} poker tools:")
    for tool_func in tools:
        print(f"\n{tool_func.name}:")
        print(f"  {tool_func.description[:100]}...")

    # Test pot odds tool
    print("\n" + "="*60)
    print("Testing pot odds calculation:")
    pot_odds_tool = [t for t in tools if t.name == "calculate_pot_odds"][0]
    result = pot_odds_tool.invoke("100,25")
    print(result)
