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
# debugging_map = {True:f"T", False:f"F"}
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

phase_map = {"Pre-Flop":"Flop", "Flop":"Turn", "Turn":"River"}

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
        return f"{val}"

# ---------------------
# 3. Poker Environment
# ---------------------
MAX_NUM_PLAYERS = 9

class PokerEnv:
    def __init__(self, num_players, endowment, small_blind=10, big_blind=20, ante=0):
        self.deck = shuffled_deck()
        self.hands = []
        self.community_cards = []
        
        self.active_players = [True] * num_players
        self.can_act = [True] * num_players
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
        
        self.actions = f"Preflop:\n("
        self.active_players_str = []

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

                if self.money[i] == 0:
                    self.can_act[i] = False
            print(f"All players post ante of {self.ante_amount}.")

        # --- Small Blind ---
        if self.money[sb_pos] < self.small_blind_amount:
            print(f"Player {sb_pos+1} doesn't have enough for small blind. Reloading stack (+{self.endowment}).")
            self.money[sb_pos] += self.endowment

        sb_paid = min(self.money[sb_pos], self.small_blind_amount)
        self.money[sb_pos] -= sb_paid
        self.bets[sb_pos] += sb_paid
        self.pot += sb_paid

        if self.money[sb_pos] == 0:
            self.can_act[i] = False

        # --- Big Blind ---
        if self.money[bb_pos] < self.big_blind_amount:
            print(f"Player {bb_pos+1} doesn't have enough for big blind. Reloading stack (+{self.endowment}).")
            self.money[bb_pos] += self.endowment

        bb_paid = min(self.money[bb_pos], self.big_blind_amount)
        self.money[bb_pos] -= bb_paid
        self.bets[bb_pos] += bb_paid
        self.pot += bb_paid

        if self.money[bb_pos] == 0:
             self.can_act[i] = False

        print(f"Player {sb_pos+1} posts small blind of {sb_paid}.")
        print(f"Player {bb_pos+1} posts big blind of {bb_paid}.")

        # Set initial current bet to big blind
        for i in range(self.num_players):
            self.current_bet[i] = self.bets[i]

    def rebuy(self):
        for i in range(self.num_players):
            if self.money[i] < 1000:
                rebuy = 1000 - self.money[i]
                self.net[i] -= rebuy
                self.money[i] += rebuy

    def deal(self, num_players):
        self.deck = shuffled_deck()
        self.actions = f"Preflop:\n("
        self.active_players_str = []
        self.can_act = [True] * num_players
        self.hands = [[self.deck.pop(), self.deck.pop()] for _ in range(num_players)]
        self.active_players = [True] * num_players
        self.played = [False] * num_players
        self.bets = [0] * num_players
        self.current_bet = [0] * num_players
        self.pot = 0
        self.community_cards = []
        self.rebuy()
        self.rotate_positions()
        self.post_blinds_and_antes()

    def next_round(self):
        self.actions += f")\n{phase_map[phase(len(self.community_cards))]}:\n("
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

    # Returns Poker Round Context
    def get_state(self, player_id):
        hand = self.hands[player_id]
        comm = self.community_cards
        """
        state: length: 28 + 3(MAX_NUM_PLAYERS-2) = 46 | for MAX_NUM_PLAYERS >= 2

        """
        state = [card[0] for card in hand + comm] + [card[1] for card in hand + comm] + [0]*(14 - len(hand + comm))
        state += [player_id] + [self.dealer_position] + [self.big_blind_amount] + [self.small_blind_amount] + self.active_players + [0]*(MAX_NUM_PLAYERS - len(self.active_players))
        state += [self.pot, self.current_bet[player_id]] + self.bets + [0]*(MAX_NUM_PLAYERS - len(self.bets))
        state += self.money + [0]*(MAX_NUM_PLAYERS - len(self.money))
        self.states += state

        return np.array(state, dtype=np.float32)
    
    def show_state(self):
        print("\n===================================")
        print(f"Phase: {phase(len(self.community_cards))}")
        for i in range(len(self.active_players)):
            print(f"(In-hand: {self.active_players[i]}, Can-act: {self.can_act[i]}) Player {i+1}'s hand:")
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

        # Block illegal re-actions in the same round
        if self.played[player_id]:
            print(f"Illegal: Player {player_id+1} already acted this round without new raise — forced to fold.")
            self.active_players[player_id] = False
            self.can_act[player_id] = False
            self.actions += f"(Illegal), "
            if self.active_players.count(True) <= 1:
                self.game_over = True
            return

        if not self.active_players[player_id] or not self.can_act[player_id]:
            return

        # self.active_players_str += [f"{i+1}:" + debugging_map[self.active_players[i]] for i in range(self.num_players)]
        if (action_map[action] == "Raise"):
            self.actions += f"Player {player_id+1} {action_map[action]}d {raise_amount}, "
        else:
            self.actions += f"Player {player_id+1} {action_map[action]}ed, "
        # self.actions += f"Player {player_id+1} {action_map[action]}ed, "

        # mark as having acted (whether legal or illegal)
        self.played[player_id] = True

        # ---------- Validate obvious illegal inputs first ----------
        if action == 3:
            # raise must be strictly positive
            if raise_amount <= 0:
                print(f"Illegal action: Player {player_id+1} attempted to raise by {raise_amount} (must be > 0). Penalized: forced to fold.")
                # self.active_players[player_id] = False
                target_bet = self.money[player_id]
                self.can_act[player_id] = False
                self.actions += f"(Illegal), "
                self.bet(target_bet, player_id)
                if self.active_players.count(True) <= 1:
                    self.game_over = True
                return

        # Fold
        if action == 0:
            self.active_players[player_id] = False
            self.can_act[player_id] = False
            if self.active_players.count(True) <= 1:
                self.game_over = True
            return
        
        # Check
        elif action == 1:
            highest_bet = max(self.bets) # if any(self.bets) else 0
            # If there is a higher bet than player's bet, check is invalid (unless player has no chips)
            if highest_bet > self.bets[player_id]:
                print(f"Invalid Check | There is a higher bet. Player {player_id+1} penalized: forced to go all-in.")
                # self.active_players[player_id] = False
                target_bet = self.money[player_id]
                self.can_act[player_id] = False
                self.actions += f"(Illegal), "
                self.bet(target_bet, player_id)
                # if self.active_players.count(True) <= 1:
                #     self.game_over = True
                return

        # Call
        elif action == 2:
            highest_bet = max(self.bets) # if any(self.bets) else 0
            to_call = highest_bet - self.bets[player_id]
            # If nothing to call, then call is illegal (player should check or raise). Penalize.
            if to_call <= 0:
                print(f"Invalid Call | Nothing to call for Player {player_id+1} (to_call={to_call}). Penalized: forced to go all-in.")
                # self.active_players[player_id] = False
                target_bet = self.money[player_id]
                self.can_act[player_id] = False
                self.actions += f"(Illegal), "
                self.bet(target_bet, player_id)
                # if sum(1 for x in self.active_players if x) <= 1:
                #     self.game_over = True
                return

            call_amount = min(to_call, self.money[player_id])
            prev_current_bet = self.current_bet[player_id]
            self.current_bet[player_id] += call_amount
            diff = self.current_bet[player_id] - prev_current_bet

            self.bets[player_id] += diff
            self.pot += diff
            self.money[player_id] -= diff

            if self.money[player_id] == 0:
                self.can_act[player_id] = False
        
        # Raise
        elif action == 3:
            highest_bet = max(self.bets) if any(self.bets) else 0
            target_bet = highest_bet + raise_amount 
            # If target equals highest and player still has chips, treat as illegal (raise must increase)
            if target_bet == highest_bet and self.money[player_id] > 0:
                print(f"Invalid Raise | Cannot raise by zero. Player {player_id+1} penalized: forced to go all-in.")
                # self.active_players[player_id] = False
                target_bet = self.money[player_id]
                self.can_act[player_id] = False
                self.actions += f"(Illegal), "
                self.bet(target_bet, player_id)
                # if sum(1 for x in self.active_players if x) <= 1:
                #     self.game_over = True
                return

            self.bet(target_bet, player_id)

    def bet(self, target_bet, player_id):
        diff = target_bet - self.bets[player_id]

        # protect against negative diff or over-withdraw
        diff = max(diff, 0)
        actual_diff = min(diff, self.money[player_id])

        self.money[player_id] -= actual_diff
        self.bets[player_id] += actual_diff
        # Update player's recorded current bet to the target they attempted (even if all-in clipped)
        self.current_bet[player_id] = self.bets[player_id]
        self.pot += actual_diff

        if self.money[player_id] == 0:
            self.can_act[player_id] = False

        # reset other players' played flags so they must respond to this new raise (but only those still active and with chips)
        # Reset action flags only for opponents who are still in-hand and can respond
        for i in range(self.num_players):
            if i != player_id and self.active_players[i] and self.can_act[i]:
                self.played[i] = False
        # Mark raiser as having acted
        self.played[player_id] = True

    def is_round_done(self):
        """
        Returns True when the betting round is complete (everyone in-hand who can act has acted
        and no player that can act owes a call). Also sets self.game_over=True if only one player remains in-hand
        OR if no players can act (we'll fast-forward to showdown in that case).
        """
        # Count players still in the hand (not folded)
        in_hand_count = sum(1 for a in self.active_players if a)
        # Count players who can act (not folded AND not all-in)
        can_act_count = sum(1 for i in range(self.num_players) if self.active_players[i] and self.can_act[i])

        # If only one player remains in-hand, round done -> immediate finish
        if in_hand_count <= 1:
            self.game_over = True
            print("Round done because only one player remains in hand.")
            return True

        # If nobody can act (all remaining are all-in), finish the betting (fast-forward)
        if can_act_count == 0:
            self.game_over = True
            print("Round done because no players can act (all remaining players are all-in).")
            return True

        # Otherwise check if all players who can act have either played
        action_finished = all(
            (not self.active_players[i]) or (not self.can_act[i]) or self.played[i]
            for i in range(self.num_players)
        )
        print(f"Played flags: {self.played}, In-hand: {self.active_players}, Can-act: {self.can_act}, Money: {self.money}, Action finished: {action_finished}")

        if not action_finished:
            return False

        # Are bets balanced among players who can act (i.e., no player with chips who still owes a call)?
        max_bet = max(self.bets) if any(self.bets) else 0
        for i in range(self.num_players):
            if not self.active_players[i] or not self.can_act[i]:
                continue
            to_call = max_bet - self.bets[i]
            # if a player who can act still owes money and has chips to call, round isn't done
            if to_call > 0 and self.money[i] > 0:
                print(f"Player {i+1} still can call {to_call} -> round not finished")
                return False

        # If we get here: everyone in-hand who can act has responded AND no actionable calls remain
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
            self.money[i] = total_won[i]
            money_change = [total_won[i] - self.bets[i] for i in range(len(total_won))]
            # print(f"{money_change}, {self.net}")
            self.net[i] += money_change[i]
        
        # self.result = [self.net[i] - self.endowment*self.reload[i] for i in range(self.num_players)]
        print("\nCommunity cards:")
        if self.community_cards:
            for c in self.community_cards:
                print(" ", card_name(c))
        else:
            print("\nFinal Results:")
        for i in range(self.num_players):
            print(f"Player {i+1}: Result: {self.net[i] + self.money[i] - 1000}, Net: {self.net[i]}, Money = {self.money[i]} ({money_change[i]})")
            self.money[i] = self.endowment

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

        # if no one can act (all remaining are all-in), finish community cards and go to showdown
        if sum(1 for i in range(env.num_players) if env.active_players[i] and env.can_act[i]) == 0:
            print("No players can act — fast-forwarding remaining community cards to showdown.")
            # fill community to river
            while len(env.community_cards) < 5:
                env.next_round()
            break

        while not env.is_round_done():
            for pid in range(NUM_PLAYERS):
                if not env.active_players[pid] or not env.can_act[pid] or env.played[pid]:
                    continue

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
    print(f"Result Sum: {sum(env.result)}")
    print(f"Small Blind: Player {(env.dealer_position + 1) % env.num_players + 1}, Big Blind: Player {(env.dealer_position + 2) % env.num_players + 1}")
    # for i in range (env.num_players):
    #     print(f"{env.active_players_str[i]}")
    print(f"Action: {env.actions}")

NUM_PLAYERS = 6
ENDOWMENT = 1000

env = PokerEnv(NUM_PLAYERS, ENDOWMENT)
for hand in range(100):  # play 5 hands
    print(f"\n=== HAND {hand+1} ===")
    play()