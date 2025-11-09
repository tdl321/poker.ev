"""
Debug-enabled Pygame GUI for poker.ev

This extends the regular GUI with:
- Automatic hand saving to Pinecone
- Debug overlay showing storage status
- Console logging for all Pinecone operations
"""

import pygame
import time
from datetime import datetime
from typing import Optional
from texasholdem import HandPhase

from poker_ev.gui.pygame_gui import PygameGUI
from poker_ev.memory.hand_history import HandHistory
from poker_ev.engine.game_wrapper import PokerGame
from poker_ev.agents.agent_manager import AgentManager


class PygameGUIDebug(PygameGUI):
    """
    Debug version of Pygame GUI with Pinecone integration
    """

    def __init__(self, game: PokerGame, agent_manager: AgentManager,
                 window_size: tuple = (1400, 900), enable_chat: bool = True,
                 hand_history: Optional[HandHistory] = None):
        """
        Initialize debug GUI with hand history tracking

        Args:
            game: PokerGame instance
            agent_manager: AgentManager for AI players
            window_size: (width, height) of the window
            enable_chat: Enable AI poker advisor chat panel
            hand_history: HandHistory instance for Pinecone storage
        """
        super().__init__(game, agent_manager, window_size, enable_chat)

        # Hand history for Pinecone storage
        self.hand_history = hand_history or HandHistory()

        # Debug state
        self.debug_overlay_visible = True
        self.last_save_status = None
        self.last_save_time = None
        self.hands_saved_count = 0

        # Hand tracking
        self.current_hand_id = None
        self.hand_start_time = None
        self.hand_start_state = None
        self.player_starting_chips = {}

        print("\n" + "=" * 70)
        print("🐛 DEBUG MODE ENABLED")
        print("=" * 70)
        print("Features:")
        print("  ✓ Automatic hand saving to Pinecone after each hand")
        print("  ✓ Debug overlay (press 'D' to toggle)")
        print("  ✓ Console logging for all storage operations")
        print("=" * 70)
        print()

    def format_card(self, card_obj) -> str:
        """Format a card object to readable string"""
        rank_map = {
            0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7', 6: '8',
            7: '9', 8: 'T', 9: 'J', 10: 'Q', 11: 'K', 12: 'A'
        }
        suit_map = {1: '♠', 2: '♥', 4: '♦', 8: '♣'}

        if hasattr(card_obj, 'rank') and hasattr(card_obj, 'suit'):
            return f"{rank_map.get(card_obj.rank, '?')}{suit_map.get(card_obj.suit, '?')}"
        return str(card_obj)

    def handle_events(self):
        """Override to add debug key handling"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Add debug overlay toggle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.debug_overlay_visible = not self.debug_overlay_visible
                    print(f"🐛 Debug overlay: {'ON' if self.debug_overlay_visible else 'OFF'}")

            # Pass to normal event handler
            if hasattr(self, 'event_handler'):
                self.event_handler.handle_event(event)

        return True

    def track_hand_start(self, state):
        """Track when a new hand starts"""
        if state['hand_active'] and self.current_hand_id is None:
            self.current_hand_id = f"hand_{int(time.time())}_{state.get('current_player', 0)}"
            self.hand_start_time = datetime.now()
            self.hand_start_state = state.copy()

            # Save starting chips for profit calculation
            self.player_starting_chips = {
                i: p['chips'] for i, p in enumerate(state['players'])
            }

            print(f"\n{'='*70}")
            print(f"🎴 NEW HAND STARTED: {self.current_hand_id}")
            print(f"{'='*70}")
            print(f"Time: {self.hand_start_time.strftime('%H:%M:%S')}")
            print(f"Phase: {state['hand_phase']}")
            print(f"Pot: ${state['pot']}")

            # Show player 0 cards
            player_0 = state['players'][0]
            if player_0.get('hand'):
                cards_str = ', '.join([self.format_card(c) for c in player_0['hand']])
                print(f"Your cards: {cards_str}")
            print(f"{'='*70}\n")

    def track_hand_end(self, state):
        """Track when a hand ends and save to Pinecone"""
        # Hand ended if it was active and now isn't
        if not state['hand_active'] and self.current_hand_id is not None:
            print(f"\n{'='*70}")
            print(f"🏁 HAND COMPLETED: {self.current_hand_id}")
            print(f"{'='*70}")

            # Prepare hand data
            hand_data = self._prepare_hand_data(state)

            # Save to Pinecone
            print(f"💾 Saving hand to Pinecone...")
            try:
                success = self.hand_history.save_hand(hand_data)

                if success:
                    self.hands_saved_count += 1
                    self.last_save_status = "SUCCESS"
                    self.last_save_time = datetime.now()
                    print(f"✅ Hand saved successfully!")
                    print(f"   Total hands saved: {self.hands_saved_count}")
                else:
                    self.last_save_status = "FAILED"
                    print(f"❌ Failed to save hand")

            except Exception as e:
                self.last_save_status = f"ERROR: {str(e)[:50]}"
                print(f"❌ Error saving hand: {e}")

            print(f"{'='*70}\n")

            # Reset hand tracking
            self.current_hand_id = None
            self.hand_start_time = None
            self.hand_start_state = None

    def _prepare_hand_data(self, end_state) -> dict:
        """Prepare hand data for Pinecone storage"""
        start_state = self.hand_start_state or {}

        # Get player 0 data
        player_0_start = start_state.get('players', [{}])[0]
        player_0_end = end_state.get('players', [{}])[0]

        # Format cards
        your_cards = []
        if player_0_start.get('hand'):
            your_cards = [self.format_card(c) for c in player_0_start['hand']]

        board_cards = []
        if end_state.get('board'):
            board_cards = [self.format_card(c) for c in end_state['board']]

        # Calculate profit
        start_chips = self.player_starting_chips.get(0, 1000)
        end_chips = player_0_end.get('chips', start_chips)
        profit = end_chips - start_chips

        # Determine outcome
        outcome = 'unknown'
        if player_0_end.get('folded'):
            outcome = 'folded'
        elif profit > 0:
            outcome = 'won'
        elif profit < 0:
            outcome = 'lost'
        else:
            outcome = 'push'

        # Build hand data
        hand_data = {
            'hand_id': self.current_hand_id,
            'timestamp': self.hand_start_time.isoformat() if self.hand_start_time else datetime.now().isoformat(),
            'your_cards': your_cards,
            'board': board_cards,
            'pot': end_state.get('pot', 0),
            'phase': str(end_state.get('hand_phase', 'unknown')),
            'position': self._determine_position(0, start_state),
            'outcome': outcome,
            'profit': profit,
            'actions_summary': f"Hand completed at {datetime.now().strftime('%H:%M:%S')}",
            'notes': f"Debug mode hand. Started: {self.hand_start_time.strftime('%H:%M:%S') if self.hand_start_time else 'unknown'}",
            'hand_strength': self._estimate_hand_strength(your_cards),
            'board_texture': self._analyze_board_texture(board_cards)
        }

        # Log the data
        print(f"\n📋 Hand Data:")
        print(f"   Cards: {', '.join(your_cards) if your_cards else 'None'}")
        print(f"   Board: {', '.join(board_cards) if board_cards else 'None'}")
        print(f"   Outcome: {outcome}")
        print(f"   Profit: ${profit:+d}")
        print(f"   Pot: ${hand_data['pot']}")

        return hand_data

    def _determine_position(self, player_idx: int, state: dict) -> str:
        """Determine player position (simplified)"""
        # This is a simplified version - actual position depends on button
        positions = ['Button', 'Small Blind', 'Big Blind', 'UTG', 'Middle', 'Cutoff']
        return positions[player_idx % len(positions)]

    def _estimate_hand_strength(self, cards: list) -> str:
        """Estimate hand strength (simplified)"""
        if not cards or len(cards) < 2:
            return 'Unknown'

        # Very simplified hand strength
        ranks = [c[0] for c in cards if len(c) > 0]

        if 'A' in ranks:
            return 'Strong' if len(set(ranks)) == 1 or 'K' in ranks or 'Q' in ranks else 'Medium'
        elif 'K' in ranks or 'Q' in ranks:
            return 'Medium'
        else:
            return 'Weak'

    def _analyze_board_texture(self, board: list) -> str:
        """Analyze board texture (simplified)"""
        if not board:
            return 'Preflop'
        elif len(board) <= 2:
            return 'Early'
        elif len(board) == 3:
            return 'Flop'
        elif len(board) == 4:
            return 'Turn'
        else:
            return 'River'

    def render_debug_overlay(self):
        """Render debug overlay showing Pinecone status"""
        if not self.debug_overlay_visible:
            return

        # Create semi-transparent overlay surface
        overlay_width = 350
        overlay_height = 200
        overlay_x = 10
        overlay_y = 10

        # Background
        overlay_surf = pygame.Surface((overlay_width, overlay_height))
        overlay_surf.set_alpha(220)
        overlay_surf.fill((20, 20, 20))

        # Border
        pygame.draw.rect(overlay_surf, (100, 100, 100), overlay_surf.get_rect(), 2)

        # Font
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)

        # Title
        title = font.render("🐛 DEBUG INFO", True, (255, 255, 0))
        overlay_surf.blit(title, (10, 10))

        # Pinecone status
        y = 45
        status_text = small_font.render("Pinecone Status:", True, (200, 200, 200))
        overlay_surf.blit(status_text, (10, y))

        # Connection status
        y += 25
        conn_color = (0, 255, 0) if self.hand_history else (255, 0, 0)
        conn_text = "CONNECTED" if self.hand_history else "DISCONNECTED"
        conn = small_font.render(f"  Connection: {conn_text}", True, conn_color)
        overlay_surf.blit(conn, (10, y))

        # Hands saved
        y += 25
        saved = small_font.render(f"  Hands Saved: {self.hands_saved_count}", True, (200, 200, 200))
        overlay_surf.blit(saved, (10, y))

        # Current hand status
        y += 25
        if self.current_hand_id:
            hand_status = small_font.render(f"  Current Hand: Active", True, (0, 255, 0))
        else:
            hand_status = small_font.render(f"  Current Hand: None", True, (150, 150, 150))
        overlay_surf.blit(hand_status, (10, y))

        # Last save status
        y += 25
        if self.last_save_status:
            status_color = (0, 255, 0) if self.last_save_status == "SUCCESS" else (255, 100, 100)
            last_save = small_font.render(f"  Last Save: {self.last_save_status}", True, status_color)
            overlay_surf.blit(last_save, (10, y))

        # Instructions
        y += 35
        instructions = small_font.render("Press 'D' to toggle", True, (150, 150, 150))
        overlay_surf.blit(instructions, (10, y))

        # Blit to main screen
        self.screen.blit(overlay_surf, (overlay_x, overlay_y))

    def render(self):
        """Override render to add debug overlay and hand tracking"""
        # Get game state
        state = self.game.get_game_state()

        # Track hand lifecycle
        self.track_hand_start(state)
        self.track_hand_end(state)

        # Call parent render
        super().render()

        # Add debug overlay
        self.render_debug_overlay()

    def run(self):
        """Override run to use our custom render and event handling"""
        clock = pygame.time.Clock()
        running = True

        # Start first hand
        if not self.game.is_hand_running():
            self.game.start_new_hand()

        while running:
            # Handle events (use our custom handler)
            running = self.handle_events()

            # Update game state
            state = self.game.get_game_state()

            # Let AI agents play if it's their turn
            if state['hand_active'] and state['current_player'] is not None:
                current = state['current_player']
                if current != 0:  # Not human player
                    self.agent_manager.take_action(current, state, self.game)

            # Check if hand should start
            if not state['hand_active']:
                # Small delay before starting next hand
                pygame.time.wait(2000)
                self.game.start_new_hand()

            # Render everything (includes our tracking)
            self.render()

            # Cap at 60 FPS
            clock.tick(60)

        pygame.quit()
