import random
import sys
import numpy as np
from collections import Counter

# ---------------------
# Seed Saver
# ---------------------
current_seed = None
def custom_exception_hook(exc_type, exc_value, tb):
    """
    A custom exception hook to print the current random seed on error.
    """
    global current_seed
    if current_seed is not None:
        print(f"\nFATAL ERROR: The random seed used for this run was: {current_seed}", file=sys.stderr)

# ---------------------
# 1. Deck
# ---------------------
suits_map = {1:"Spade", 2:"Heart", 3:"Diamond", 4:"Club"}
suits = [1, 2, 3, 4]
ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
standard_deck = [(rank, suit) for rank in ranks for suit in suits]
action_map = {0:"Fold", 1:"Check", 2:"Call", 3:"Raise"}
# print(f"{standard_deck.pop()},\n {standard_deck}")

# ---------------------
# 2. Shuffler
# ---------------------
def shuffled_deck():
    deck = standard_deck.copy()
    random.shuffle(deck)
    return deck

# -----------------------
# Simple hand evaluator (rank only, no real poker rules)
# -----------------------
def hand_strength(cards):
    """
    Computes a simple numeric hand strength for a list of cards.
    cards: list of (rank, suit), rank=2-14 (Ace=14)
    Returns an integer score: higher = stronger.
    """

    # No cards -> weakest possible
    if not cards:
        return 0

    # Convert ranks and suits
    ranks = [card[0] for card in cards]
    suits = [card[1] for card in cards]

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    unique_ranks = sorted(set(ranks), reverse=True)

    # Check for flush
    flush_suit = None
    for s, count in suit_counts.items():
        if count >= 5:
            flush_suit = s
            break

    # Check for straight (Ace can be high or low)
    sorted_ranks = sorted(set(ranks))
    # allow Ace low straight
    if 14 in sorted_ranks:
        sorted_ranks = [1] + sorted_ranks

    straights = []
    for i in range(len(sorted_ranks) - 4):
        if sorted_ranks[i+4] - sorted_ranks[i] == 4:
            straights.append(sorted_ranks[i+4])  # highest card of straight

    straight_high = max(straights) if straights else 0

    # Check for straight flush
    straight_flush_high = 0
    if flush_suit:
        flush_cards = [card[0] for card in cards if card[1] == flush_suit]
        flush_ranks = sorted(set(flush_cards))
        if 14 in flush_ranks:
            flush_ranks = [1] + flush_ranks
        for i in range(len(flush_ranks) - 4):
            if flush_ranks[i+4] - flush_ranks[i] == 4:
                straight_flush_high = flush_ranks[i+4]

    # Determine hand type and score
    # Hand ranking (high score = strong):
    # 9: Straight Flush, 8: Four of a Kind, 7: Full House, 6: Flush,
    # 5: Straight, 4: Three of a Kind, 3: Two Pair, 2: One Pair, 1: High Card

    counts = sorted(rank_counts.values(), reverse=True)
    # pad to avoid index errors when there is only one distinct rank
    if len(counts) < 2:
        counts += [0] * (2 - len(counts))

    hand_type = 0
    tiebreaker = 0

    # helper to get ranks by count
    def ranks_with_count(min_count):
        return sorted([r for r, c in rank_counts.items() if c >= min_count], reverse=True)

    if straight_flush_high:
        hand_type = 9
        tiebreaker = straight_flush_high
    elif counts[0] == 4:
        hand_type = 8
        quad_ranks = ranks_with_count(4)
        quad_rank = quad_ranks[0] if quad_ranks else 0
        tiebreaker = quad_rank
    elif counts[0] == 3 and counts[1] >= 2:
        hand_type = 7
        trip_ranks = ranks_with_count(3)
        trip_rank = trip_ranks[0] if trip_ranks else 0
        pair_candidates = [r for r, c in rank_counts.items() if c >= 2 and r != trip_rank]
        pair_rank = max(pair_candidates) if pair_candidates else 0
        tiebreaker = trip_rank * 15 + pair_rank
    elif flush_suit:
        hand_type = 6
        # sum top 5 flush card ranks as tiebreaker (fallback to sum of what's available)
        flush_ranks = sorted([r for r, s in cards if s == flush_suit], reverse=True)[:5]
        tiebreaker = sum(flush_ranks)
    elif straight_high:
        hand_type = 5
        tiebreaker = straight_high
    elif counts[0] == 3:
        hand_type = 4
        trip_ranks = ranks_with_count(3)
        trip_rank = trip_ranks[0] if trip_ranks else 0
        tiebreaker = trip_rank
    elif counts[0] == 2 and counts[1] == 2:
        hand_type = 3
        pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
        # ensure there are at least two pairs
        if len(pairs) >= 2:
            tiebreaker = pairs[0] * 15 + pairs[1]
        else:
            tiebreaker = pairs[0] * 15 if pairs else 0
    elif counts[0] == 2:
        hand_type = 2
        pair_ranks = ranks_with_count(2)
        pair_rank = pair_ranks[0] if pair_ranks else 0
        tiebreaker = pair_rank
    else:
        hand_type = 1
        tiebreaker = max(ranks) if ranks else 0

    # Final numeric score
    score = hand_type * 100 + tiebreaker  # hand type is primary, tiebreaker resolves ties
    return score

def card_name(card):
    rank, suit = card
    rank_name = {11:"J", 12:"Q", 13:"K", 14:"A"}.get(rank, str(rank))
    suit_name = suits_map[suit]
    return f"{rank_name} of {suit_name}s"



def phase(val):
    if val == 0:
        return "Pre-Flop"
    elif val == 3:
        return "Flop"
    elif val == 4:
        return "Turn"
    elif val == 5:
        return "River"
    else:
        return "{val}"

# ---------------------
# 3. Poker Environment
# ---------------------
MAX_NUM_PLAYERS = 9

class PokerEnv:
    def __init__(self, num_players, endowment, small_blind=10, big_blind=20, ante=0):
        self.deck = shuffled_deck()
        self.hands = []
        self.active_players = [True] * num_players
        self.community_cards = []
        self.num_players = num_players
        self.played = [False] * num_players
        self.pot = 0

        self.dealer_position = 0
        self.small_blind_amount = small_blind
        self.big_blind_amount = big_blind
        self.ante_amount = ante

        self.bets = [0] * num_players
        self.current_bet = [0] * num_players
        self.bet_history = []
        self.states = []

        self.endowment = endowment
        self.money = [endowment] * num_players
        self.reload = [0] * num_players
        self.net = [0] * num_players
        self.result = [0] * num_players

        self.game_over = False

    def rotate_positions(self):
        """Rotate dealer and blinds for the next hand."""
        self.dealer_position = (self.dealer_position + 1) % self.num_players

    def post_blinds_and_antes(self):
        """Automatically post blinds and antes before each new hand."""
        sb_pos = (self.dealer_position + 1) % self.num_players
        bb_pos = (self.dealer_position + 2) % self.num_players

        # Everyone posts ante (if any)
        if self.ante_amount > 0:
            for i in range(self.num_players):
                if self.money[i] < self.ante_amount:
                    print(f"Player {i+1} doesn't have enough for ante. Reloading stack (+{self.endowment}).")
                    self.money[i] += self.endowment  # reload bankroll
                
                ante_paid = min(self.money[i], self.ante_amount)
                self.money[i] -= ante_paid
                self.bets[i] += ante_paid
                self.pot += ante_paid
            print(f"All players post ante of {self.ante_amount}.")

        # --- Small Blind ---
        if self.money[sb_pos] < self.small_blind_amount:
            print(f"Player {sb_pos+1} doesn't have enough for small blind. Reloading stack (+{self.endowment}).")
            self.money[sb_pos] += self.endowment

        sb_paid = min(self.money[sb_pos], self.small_blind_amount)
        self.money[sb_pos] -= sb_paid
        self.bets[sb_pos] += sb_paid
        self.pot += sb_paid

        # --- Big Blind ---
        if self.money[bb_pos] < self.big_blind_amount:
            print(f"Player {bb_pos+1} doesn't have enough for big blind. Reloading stack (+{self.endowment}).")
            self.money[bb_pos] += self.endowment

        bb_paid = min(self.money[bb_pos], self.big_blind_amount)
        self.money[bb_pos] -= bb_paid
        self.bets[bb_pos] += bb_paid
        self.pot += bb_paid

        print(f"Player {sb_pos+1} posts small blind of {sb_paid}.")
        print(f"Player {bb_pos+1} posts big blind of {bb_paid}.")

        # Set initial current bet to big blind
        for i in range(self.num_players):
            self.current_bet[i] = self.bets[i]

    def deal(self, num_players):
        self.deck = shuffled_deck()
        self.hands = [[self.deck.pop(), self.deck.pop()] for _ in range(num_players)]
        self.active_players = [True] * num_players
        self.played = [False] * num_players
        self.bets = [0] * num_players
        self.current_bet = [0] * num_players
        self.pot = 0
        self.community_cards = []
        self.post_blinds_and_antes()

    def next_round(self):
        # Flop
        if len(self.community_cards) == 0:
            self.deck.pop()
            self.community_cards += [self.deck.pop(), self.deck.pop(), self.deck.pop()]

        # Turn
        elif len(self.community_cards) == 3:
            self.deck.pop()
            self.community_cards.append(self.deck.pop())

        # River
        elif len(self.community_cards) == 4:
            self.deck.pop()
            self.community_cards.append(self.deck.pop())
        
        else:
            print(f"Invalid Number of Community Cards: {len(self.community_cards)}")
            sys.exit(1)
    
    # def game_over()

    # Returns Poker Round Context
    def get_state(self, player_id):
        hand = self.hands[player_id]
        comm = self.community_cards
        """
        state: Fixed length vector representing game state
        Cards are padded to max 7 cards (2 hand + 5 community)
        """
        # Combine hand and community cards
        all_cards = hand + comm

        # Extract ranks and suits, pad to 7 cards total
        ranks = [card[0] for card in all_cards] + [0] * (7 - len(all_cards))
        suits = [card[1] for card in all_cards] + [0] * (7 - len(all_cards))

        # Build state vector with fixed size
        state = ranks + suits  # 7 + 7 = 14 elements
        state += [player_id]  # 1 element
        state += self.active_players + [0]*(MAX_NUM_PLAYERS - len(self.active_players))  # MAX_NUM_PLAYERS elements
        state += [self.pot, self.current_bet[player_id]]  # 2 elements
        state += self.bets + [0]*(MAX_NUM_PLAYERS - len(self.bets))  # MAX_NUM_PLAYERS elements
        state += self.money + [0]*(MAX_NUM_PLAYERS - len(self.money))  # MAX_NUM_PLAYERS elements

        # Total: 14 + 1 + 9 + 2 + 9 + 9 = 44 elements
        return np.array(state, dtype=np.float32)
    
    def show_state(self):
        print("\n===================================")
        print(f"Phase: {phase(len(self.community_cards))}")
        for i in range(len(self.active_players)):
            print(f"(Active: {self.active_players[i]}) Player {i+1}'s hand:")
            for c in self.hands[i]:
                print(" ", card_name(c))
            # print("Strength:", hand_strength(self.hands[i] + self.community_cards))
        print("Community cards:")
        if self.community_cards:
            for c in self.community_cards:
                print(" ", card_name(c))
        else:
            print("  (none yet)")
        print(f"Current pot: {self.pot}")
        print("===================================")

    # Called when Player is Required to Act
    def take_action(self, player_id, action, raise_amount=0):
        """
        actions: 0=fold, 1=check, 2=call, 3=raise
        Illegal moves cause immediate fold (penalty).
        """
        if not self.active_players[player_id]:
            return

        # mark as having acted (whether legal or illegal)
        self.played[player_id] = True

        # ---------- Validate obvious illegal inputs first ----------
        if action == 3:
            # raise must be strictly positive
            if raise_amount <= 0:
                print(f"Illegal action: Player {player_id+1} attempted to raise by {raise_amount} (must be > 0). Penalized: forced to fold.")
                self.active_players[player_id] = False
                if self.active_players.count(True) <= 1:
                    self.game_over = True
                return

        # Fold
        if action == 0:
            self.active_players[player_id] = False
            if self.active_players.count(True) <= 1:
                self.game_over = True
            return
        
        # Check
        elif action == 1:
            highest_bet = max(self.bets) if any(self.bets) else 0
            # If there is a higher bet than player's bet, check is invalid (unless player has no chips)
            if highest_bet > self.bets[player_id] and self.money[player_id] > 0:
                print(f"Invalid Check | There is a higher bet. Player {player_id+1} penalized: forced to fold.")
                self.active_players[player_id] = False
                if self.active_players.count(True) <= 1:
                    self.game_over = True
                return

        # Call
        elif action == 2:
            highest_bet = max(self.bets) if any(self.bets) else 0
            to_call = highest_bet - self.bets[player_id]
            # If nothing to call, then call is illegal (player should check or raise). Penalize.
            if to_call <= 0:
                print(f"Invalid Call | Nothing to call for Player {player_id+1} (to_call={to_call}). Penalized: forced to fold.")
                self.active_players[player_id] = False
                if self.active_players.count(True) <= 1:
                    self.game_over = True
                return

            call_amount = min(to_call, self.money[player_id])
            prev_current_bet = self.current_bet[player_id]
            self.current_bet[player_id] += call_amount
            diff = self.current_bet[player_id] - prev_current_bet

            self.bets[player_id] += diff
            self.pot += diff
            self.money[player_id] -= diff
        
        # Raise
        elif action == 3:
            highest_bet = max(self.bets) if any(self.bets) else 0
            target_bet = highest_bet + raise_amount 
            # If target equals highest and player still has chips, treat as illegal (raise must increase)
            if target_bet == highest_bet and self.money[player_id] > 0:
                print(f"Invalid Raise | Cannot raise by zero. Player {player_id+1} penalized: forced to fold.")
                self.active_players[player_id] = False
                if self.active_players.count(True) <= 1:
                    self.game_over = True
                return

            diff = target_bet - self.bets[player_id]

            # protect against negative diff or over-withdraw
            diff = max(diff, 0)
            actual_diff = min(diff, self.money[player_id])

            self.money[player_id] -= actual_diff
            self.bets[player_id] += actual_diff
            # Update player's recorded current bet to the target they attempted (even if all-in clipped)
            self.current_bet[player_id] = self.bets[player_id]
            self.pot += actual_diff

            # reset other players' played flags so they must respond to this new raise (but only those still active and with chips)
            for i in range(len(self.played)):
                if (i != player_id) and self.active_players[i] and self.money[i] > 0:
                    self.played[i] = False

    def is_round_done(self):
        """
        Returns True when the betting round is complete (everyone active has acted
        and no active player with money owes a call). Also sets self.game_over=True
        if only one player remains active.
        """

        active_count = sum(1 for a in self.active_players if a)
        if active_count <= 1:
            self.game_over = True
            print("Round done because only one active player remains.")
            return True
        
        # Treat players who are active but have no chips as 'cannot act' (they are effectively all-in)
        action_finished = all(
            (not self.active_players[i]) or self.played[i] or (self.money[i] == 0)
            for i in range(self.num_players)
        )
        print(f"Played flags: {self.played}, Active players: {self.active_players}, Money: {self.money}, Action finished: {action_finished}")

        if not action_finished:
            return False
        
        # Are bets balanced among active players (i.e., no active player with money owes a call)?
        max_bet = max(self.bets) if any(self.bets) else 0
        for i in range(self.num_players):
            if not self.active_players[i]:
                continue
            to_call = max_bet - self.bets[i]
            # if an active player still owes money and has chips to call, round isn't done
            if to_call > 0 and self.money[i] > 0:
                print(f"Player {i+1} still can call {to_call} -> round not finished")
                return False

        # If we get here: everyone active has acted (or is all-in) AND no active player can or needs to call
        # Round finishes: reset played flags and current_bet for next betting round
        self.played = [False] * self.num_players
        self.current_bet = [0] * self.num_players
        print("Betting round complete: resetting played flags and current bets.")
        return True

    def showdown(self):
        for i, activate in enumerate(self.active_players):
            if activate:
                print(f"Player {i+1}'s hand:")
                for c in self.hands[i]:
                    print(" ", card_name(c))
                print("Strength:", hand_strength(self.hands[i] + self.community_cards))

        strengths = [
                hand_strength(self.hands[i] + self.community_cards) if self.active_players[i] else 0
                for i in range(self.num_players)
            ]
        if self.active_players.count(True) == 1:
            winner = self.active_players.index(True)
        else:
            winner = strengths.index(max(strengths))

        # --- Side Pot Handling ---
        # Each player's total contribution (their "cap" if all-in)
        contributions = self.bets[:]
        all_contribs = sorted(set(c for c in contributions if c > 0))
        pots = []

        last = 0
        for contrib in all_contribs:
            # players who contributed at least this much
            eligible = [i for i in range(self.num_players) if contributions[i] >= contrib]
            pot_size = (contrib - last) * len(eligible)
            pots.append({"size": pot_size, "eligible": eligible})
            last = contrib

        # --- Determine winners for each pot ---
        total_won = [0] * self.num_players
        for pot_index, pot in enumerate(pots):
            eligible_players = pot["eligible"]
            print(f"Evaluating Players {self.active_players}")
            pot_strengths = {pid: strengths[pid] for pid in eligible_players if self.active_players[pid]}
            if not pot_strengths:
                continue
            winner = max(pot_strengths, key=pot_strengths.get)
            total_won[winner] += pot["size"]
            print(f"Side Pot {pot_index+1}: {pot['size']} chips | Eligible: {[p+1 for p in eligible_players]} | Winner: Player {winner+1}")

        # Update money
        for i in range(self.num_players):
            self.money[i] += total_won[i]
            money_change = [total_won[i] - self.bets[i] for i in range(len(total_won))]
            print(f"{money_change}, {self.net}")
            self.net[i] += money_change[i]
        
        # self.result = [self.net[i] - self.endowment*self.reload[i] for i in range(self.num_players)]
        print("\nCommunity cards:")
        if self.community_cards:
            for c in self.community_cards:
                print(" ", card_name(c))
        else:
            print("\nFinal Results:")
        for i in range(self.num_players):
            print(f"Player {i+1}: Net: {self.net[i]}, Money = {self.money[i]} ({money_change[i]})")

# def main(num_players):
def play():
    env.deal(NUM_PLAYERS)
    env.show_state()

    env.get_state(1)
    env.get_state(0)
    for round in ["preflop", "flop", "turn", "river"]:
        if round != "preflop":
            env.next_round()
        env.show_state()

        while not env.is_round_done():
            for pid in range(NUM_PLAYERS):
                # if pid == 0:
                #     action = 3
                #     raise_amount=0
                # if pid == 1:
                #     action = 2
                #     raise_amount=0
                # if pid == 2:
                #     decision = random.randint(0,1)
                #     if decision == 0:
                #         action = 2
                #     elif decision == 1:
                #         action = 0
                #     raise_amount=0
                action = random.randint(1, 3)
                raise_amount = 0
                if action == 3:
                    highest_bet = max(env.bets) if any(env.bets) else 0
                    to_call = highest_bet - env.bets[pid]
                    max_raise_possible = max(env.money[pid] - max(to_call, 0), 0)

                    if max_raise_possible > 0:
                        raise_amount = random.randint(1, max_raise_possible)
                    else:
                        # cannot raise, fallback to check/call decision
                        if max(env.bets) - env.bets[pid] > 0 and env.money[pid] > 0:
                            action = 2  # call if there's something to call
                        else:
                            action = 1  # otherwise check
                        raise_amount = 0
                if not env.is_round_done():
                    print(f"Player: {pid}, Action({action}): {action_map[action]}, Raise_Amount: {raise_amount}")
                    env.take_action(pid, action, raise_amount)

        if env.active_players.count(True) <= 1:
            break  # someone folded
    env.showdown()

if __name__ == "__main__":
    NUM_PLAYERS = 2
    ENDOWMENT = 1000

    env = PokerEnv(NUM_PLAYERS, ENDOWMENT)
    for hand in range(5):  # play 5 hands
        print(f"\n=== HAND {hand+1} ===")
        play()