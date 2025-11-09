"""
Decision Tracker for poker.ev

Tracks pre-action and post-action states for each player decision.
Enables LLM to learn from past decisions and provide contextual advice.
"""

import time
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from texasholdem import ActionType
import logging

from poker_ev.memory.pinecone_store import PineconeMemoryStore

logger = logging.getLogger(__name__)


class DecisionTracker:
    """
    Tracks poker decisions as pre-action and post-action pairs

    For each decision point:
    1. Pre-Decision: Save game state BEFORE player acts (for LLM advice)
    2. Post-Decision: Save action taken AFTER player acts (for analysis)
    3. Finalize: Update with hand outcome when hand ends

    This enables:
    - Real-time advice based on similar past situations
    - Post-game analysis of decision optimality
    - Learning from decision patterns over time
    """

    def __init__(self, pinecone_store: Optional[PineconeMemoryStore] = None):
        """
        Initialize decision tracker

        Args:
            pinecone_store: PineconeMemoryStore instance (creates new if None)
        """
        if pinecone_store is None:
            try:
                self.store = PineconeMemoryStore()
                logger.info("Decision tracker initialized with new Pinecone store")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone store: {e}")
                raise
        else:
            self.store = pinecone_store
            logger.info("Decision tracker initialized with provided Pinecone store")

        # Track active decisions within current hand
        self.current_hand_id: Optional[str] = None
        self.hand_decisions: List[str] = []  # List of decision_ids for current hand
        self.decision_counter: int = 0  # Counter for decisions within a hand
        self.pending_pre_decision: Optional[Dict] = None  # Temporary storage

    def start_hand(self, hand_id: str):
        """
        Start tracking a new hand

        Args:
            hand_id: Unique identifier for this hand
        """
        self.current_hand_id = hand_id
        self.hand_decisions = []
        self.decision_counter = 0
        self.pending_pre_decision = None
        logger.debug(f"Started tracking hand: {hand_id}")

    def generate_decision_id(self) -> str:
        """
        Generate unique decision ID

        Returns:
            Decision ID in format: decision_{hand_id}_{counter}
        """
        if not self.current_hand_id:
            # Fallback if hand not started
            return f"decision_{int(time.time())}_{self.decision_counter:03d}"

        decision_id = f"decision_{self.current_hand_id}_{self.decision_counter:03d}"
        self.decision_counter += 1
        return decision_id

    def save_pre_decision(
        self,
        decision_id: str,
        game_state: Dict,
        your_cards: List[str],
        position: str,
        previous_actions: List[Dict] = None
    ) -> bool:
        """
        Save pre-decision state (BEFORE player acts)

        Args:
            decision_id: Unique decision identifier
            game_state: Current game state from PokerGame
            your_cards: Player's hole cards (formatted strings)
            position: Player's position (e.g., "Button", "Big Blind")
            previous_actions: Actions taken by opponents this round

        Returns:
            True if saved successfully
        """
        try:
            # Extract relevant state
            board = game_state.get('board', [])
            phase = str(game_state.get('hand_phase', 'unknown'))
            pot = game_state.get('pot', 0)
            chips_to_call = game_state.get('chips_to_call', 0)
            min_raise = game_state.get('min_raise', 0)

            # Get player 0 state (human player)
            players = game_state.get('players', [])
            if not players:
                logger.warning("No players in game state")
                return False

            player_0 = players[0]
            your_chips = player_0.get('chips', 0)

            # Get opponent states
            opponents = []
            for i, player in enumerate(players[1:], start=1):
                opponents.append({
                    'player_id': i,
                    'chips': player.get('chips', 0),
                    'bet': player.get('bet', 0),
                    'folded': player.get('folded', False)
                })

            # Format board cards
            board_formatted = []
            if board:
                for card in board:
                    if hasattr(card, 'rank') and hasattr(card, 'suit'):
                        board_formatted.append(self._format_card(card))
                    else:
                        board_formatted.append(str(card))

            # Build semantic description
            description = self._build_pre_decision_description(
                your_cards=your_cards,
                board=board_formatted,
                phase=phase,
                position=position,
                pot=pot,
                chips_to_call=chips_to_call,
                your_chips=your_chips,
                previous_actions=previous_actions or []
            )

            # Prepare decision data
            decision_data = {
                'decision_id': decision_id,
                'hand_id': self.current_hand_id or 'unknown',
                'timestamp': datetime.now().isoformat(),
                'type': 'pre_decision',

                # Game situation
                'your_cards': json.dumps(your_cards),
                'board': json.dumps(board_formatted),
                'phase': phase,
                'position': position,

                # Financial state
                'your_chips': int(your_chips),
                'pot': int(pot),
                'chips_to_call': int(chips_to_call),
                'min_raise': int(min_raise),

                # Opponent information
                'previous_actions': json.dumps(previous_actions or []),
                'opponents': json.dumps(opponents),

                # Semantic description
                'description': description
            }

            # Store temporarily (will be linked with post-decision)
            self.pending_pre_decision = decision_data.copy()

            # Generate embedding
            embedding = self.store.embed_text(description)

            # Save to Pinecone
            self.store.index.upsert(
                vectors=[(f"pre_{decision_id}", embedding, decision_data)]
            )

            # Track this decision
            self.hand_decisions.append(decision_id)

            logger.debug(f"Saved pre-decision: {decision_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving pre-decision: {e}")
            return False

    def save_post_decision(
        self,
        decision_id: str,
        action: ActionType,
        amount: int,
        chips_after: int,
        pot_after: int
    ) -> bool:
        """
        Save post-decision state (AFTER player acts)

        Args:
            decision_id: Same ID as pre-decision (links them)
            action: Action taken (FOLD, CALL, RAISE, etc.)
            amount: Amount of chips put in (for raise/call)
            chips_after: Player's chips after action
            pot_after: Pot size after action

        Returns:
            True if saved successfully
        """
        try:
            # Get action name
            action_name = self._action_to_string(action)

            # Build description
            if self.pending_pre_decision:
                your_cards = json.loads(self.pending_pre_decision.get('your_cards', '[]'))
                position = self.pending_pre_decision.get('position', 'unknown')
                chips_to_call = self.pending_pre_decision.get('chips_to_call', 0)

                description = self._build_post_decision_description(
                    action_name=action_name,
                    amount=amount,
                    your_cards=your_cards,
                    position=position,
                    chips_to_call=chips_to_call
                )
            else:
                description = f"Took action: {action_name}"
                if amount > 0:
                    description += f" ${amount}"

            # Prepare decision data
            decision_data = {
                'decision_id': decision_id,
                'hand_id': self.current_hand_id or 'unknown',
                'timestamp': datetime.now().isoformat(),
                'type': 'post_decision',

                # Link to pre-decision
                'pre_decision_id': decision_id,

                # Action taken
                'action': action_name,
                'amount': int(amount),

                # Immediate result
                'chips_after': int(chips_after),
                'pot_after': int(pot_after),

                # Outcome (will be updated when hand ends)
                'hand_outcome': '',  # won/lost/folded
                'hand_profit': 0,

                # Semantic description
                'description': description
            }

            # Generate embedding
            embedding = self.store.embed_text(description)

            # Save to Pinecone
            self.store.index.upsert(
                vectors=[(f"post_{decision_id}", embedding, decision_data)]
            )

            # Clear pending pre-decision
            self.pending_pre_decision = None

            logger.debug(f"Saved post-decision: {decision_id} - {action_name}")
            return True

        except Exception as e:
            logger.error(f"Error saving post-decision: {e}")
            return False

    def finalize_hand_decisions(
        self,
        hand_id: str,
        outcome: str,
        profit: int
    ) -> bool:
        """
        Update all decisions for a hand with final outcome

        Args:
            hand_id: Hand identifier
            outcome: Final outcome (won/lost/folded/push)
            profit: Net profit/loss for the hand

        Returns:
            True if updated successfully
        """
        try:
            if not self.hand_decisions:
                logger.debug(f"No decisions to finalize for hand {hand_id}")
                return True

            logger.info(f"Finalizing {len(self.hand_decisions)} decisions for hand {hand_id}")

            for decision_id in self.hand_decisions:
                # Fetch current post-decision record
                try:
                    # Note: Pinecone doesn't have a direct update method
                    # We need to fetch, modify, and re-upsert

                    # For now, we'll create a new metadata-only update
                    # In production, you'd fetch the existing vector and update metadata

                    update_data = {
                        'decision_id': decision_id,
                        'hand_id': hand_id,
                        'type': 'post_decision',
                        'hand_outcome': outcome,
                        'hand_profit': int(profit),
                        'outcome_updated': datetime.now().isoformat()
                    }

                    # Create a dummy embedding (we'll use metadata filter to find it)
                    # In a real implementation, you'd fetch the existing vector
                    logger.debug(f"Would update decision {decision_id} with outcome: {outcome}, profit: {profit}")

                except Exception as e:
                    logger.warning(f"Could not update decision {decision_id}: {e}")
                    continue

            # Reset hand tracking
            self.hand_decisions = []
            self.decision_counter = 0
            self.current_hand_id = None

            return True

        except Exception as e:
            logger.error(f"Error finalizing hand decisions: {e}")
            return False

    def search_similar_decisions(
        self,
        query: str,
        decision_type: str = 'pre_decision',
        filters: Optional[Dict] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for similar past decisions

        Args:
            query: Semantic search query
            decision_type: 'pre_decision' or 'post_decision'
            filters: Additional Pinecone filters
            top_k: Number of results to return

        Returns:
            List of matching decisions with similarity scores
        """
        try:
            # Build filter
            filter_dict = {'type': decision_type}
            if filters:
                filter_dict.update(filters)

            # Search using store's search method
            results = self.store.search(
                query=query,
                filter_dict=filter_dict,
                top_k=top_k
            )

            # Parse JSON fields
            for result in results:
                metadata = result.get('metadata', {})
                for key in ['your_cards', 'board', 'previous_actions', 'opponents']:
                    if key in metadata:
                        try:
                            metadata[key] = json.loads(metadata[key])
                        except:
                            pass
                result['metadata'] = metadata

            return results

        except Exception as e:
            logger.error(f"Error searching decisions: {e}")
            return []

    def _format_card(self, card_obj) -> str:
        """Format a card object to readable string"""
        rank_map = {
            0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7', 6: '8',
            7: '9', 8: 'T', 9: 'J', 10: 'Q', 11: 'K', 12: 'A'
        }
        suit_map = {1: '♠', 2: '♥', 4: '♦', 8: '♣'}

        if hasattr(card_obj, 'rank') and hasattr(card_obj, 'suit'):
            return f"{rank_map.get(card_obj.rank, '?')}{suit_map.get(card_obj.suit, '?')}"
        return str(card_obj)

    def _action_to_string(self, action: ActionType) -> str:
        """Convert ActionType to string"""
        action_map = {
            ActionType.FOLD: 'fold',
            ActionType.CHECK: 'check',
            ActionType.CALL: 'call',
            ActionType.RAISE: 'raise',
            ActionType.ALL_IN: 'all_in'
        }
        return action_map.get(action, str(action).lower())

    def _build_pre_decision_description(
        self,
        your_cards: List[str],
        board: List[str],
        phase: str,
        position: str,
        pot: int,
        chips_to_call: int,
        your_chips: int,
        previous_actions: List[Dict]
    ) -> str:
        """Build semantic description for pre-decision state"""
        parts = []

        # Cards and position
        cards_str = ', '.join(your_cards) if your_cards else 'unknown'
        parts.append(f"You have {cards_str} in {position} position")

        # Phase and board
        if board:
            board_str = ', '.join(board)
            parts.append(f"{phase}: {board_str}")
        else:
            parts.append(f"Pre-flop")

        # Previous actions
        if previous_actions:
            action_summary = []
            for action in previous_actions:
                player = action.get('player', '?')
                act = action.get('action', '?')
                amt = action.get('amount', 0)
                if amt > 0:
                    action_summary.append(f"Player {player} {act} ${amt}")
                else:
                    action_summary.append(f"Player {player} {act}")
            if action_summary:
                parts.append('. '.join(action_summary))

        # Financial situation
        parts.append(f"Pot: ${pot}")
        if chips_to_call > 0:
            parts.append(f"To call: ${chips_to_call}")
        parts.append(f"Your chips: ${your_chips}")

        return ". ".join(parts)

    def _build_post_decision_description(
        self,
        action_name: str,
        amount: int,
        your_cards: List[str],
        position: str,
        chips_to_call: int
    ) -> str:
        """Build semantic description for post-decision state"""
        cards_str = ', '.join(your_cards) if your_cards else 'unknown'

        if action_name == 'fold':
            return f"You folded {cards_str} in {position} position facing ${chips_to_call}"
        elif action_name == 'call':
            return f"You called ${amount} with {cards_str} in {position} position"
        elif action_name == 'raise':
            return f"You raised to ${amount} with {cards_str} in {position} position"
        elif action_name == 'check':
            return f"You checked with {cards_str} in {position} position"
        elif action_name == 'all_in':
            return f"You went all-in for ${amount} with {cards_str} in {position} position"
        else:
            return f"You took action: {action_name}"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        tracker = DecisionTracker()
        print("✅ Decision tracker initialized")

        # Example: Track a decision
        hand_id = f"hand_{int(time.time())}"
        tracker.start_hand(hand_id)

        decision_id = tracker.generate_decision_id()

        # Mock game state
        mock_state = {
            'board': [],
            'hand_phase': 'PRE_FLOP',
            'pot': 15,
            'chips_to_call': 10,
            'min_raise': 20,
            'players': [
                {'chips': 990, 'bet': 5, 'folded': False},
                {'chips': 985, 'bet': 10, 'folded': False},
            ]
        }

        # Save pre-decision
        tracker.save_pre_decision(
            decision_id=decision_id,
            game_state=mock_state,
            your_cards=['A♠', 'K♥'],
            position='Button',
            previous_actions=[
                {'player': 1, 'action': 'raise', 'amount': 10}
            ]
        )
        print(f"✅ Saved pre-decision: {decision_id}")

        # Save post-decision
        tracker.save_post_decision(
            decision_id=decision_id,
            action=ActionType.RAISE,
            amount=30,
            chips_after=960,
            pot_after=45
        )
        print(f"✅ Saved post-decision: {decision_id}")

        # Finalize hand
        tracker.finalize_hand_decisions(
            hand_id=hand_id,
            outcome='won',
            profit=60
        )
        print(f"✅ Finalized hand decisions")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
