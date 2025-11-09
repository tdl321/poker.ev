I have a Python poker engine implemented in a class `PokerEnv`. It works as follows:

- `PokerEnv(num_players, endowment, small_blind=10, big_blind=20, ante=0)`: initializes the game.
- `deal(num_players)`: deals two cards to each player, posts blinds/antes, and resets state.
- `next_round()`: progresses the game through Flop, Turn, and River.
- `get_state(player_id)`: returns a numeric vector representing the current state of the game for a player.
- `take_action(player_id, action, raise_amount=0)`: applies the action (fold=0, check=1, call=2, raise=3) and updates bets, current bet, pot, and money.
- `is_round_done()`: returns True if all players have acted and betting is complete.
- `show_state()`: prints the current state including hands, community cards, pot, and active players.
- `showdown()`: computes hand strengths, side pots, determines winners, and updates players’ money and net gains.

Other relevant details:
- Tracks `hands`, `community_cards`, `money`, `bets`, `current_bet`, `pot`, `active_players`, `played` (per-hand action tracker), and `net`.
- Supports blinds, antes, all-in, and side pot handling.

I want to create **multi-agent neural network poker players** that can interact with this environment. Requirements:

1. **Neural Network Agents**
   - Implement each agent as a PyTorch `nn.Module`.
   - Input: numeric state vector returned by `get_state(player_id)`.
   - Outputs:
     - Action logits for fold, check, call, raise (4 actions)
     - Optional logits for raise amounts (e.g., 4 buckets)
     - State value estimate (scalar)
   - Include a method `act(state, env, player_id)` that:
     - Masks illegal moves using `env.take_action()` rules or `is_valid_move()` logic
     - Samples an action probabilistically
     - Returns the selected action and optional raise amount

2. **Environment Adapter (if necessary)**
   - Wrap `PokerEnv` if needed to:
     - `reset()` → return initial numeric states for all players
     - `step(actions)` → apply actions for all players and return next_states, rewards, done
     - `legal_actions(player_id)` → return list of valid actions

3. **Reward Transformations**
   - Include three functions for risk shaping:
     - `risk_averse_reward(r)` — compress extreme rewards
     - `risk_neutral_reward(r)` — linear reward
     - `risk_seeking_reward(r)` — amplify extremes

4. **Training Loop**
   - Run multiple episodes.
   - For each episode:
     1. Reset environment and get initial states.
     2. Each agent chooses an action using `act`.
     3. Apply actions in the environment → get next states and rewards.
     4. Transform rewards using the agent’s risk function.
     5. Update agent weights via gradient ascent to maximize transformed reward.
   - Print sample rewards every N episodes.

5. **Multi-Agent Competition**
   - Agents interact via the shared `PokerEnv`.
   - Each agent maximizes its own reward, creating implicit competition.
   - Handle side pots and all-in scenarios automatically via the environment.

6. **Example Initialization**
   - 2–3 agents corresponding to risk profiles
   - Initialize `PokerEnv` with the same number of players
   - Train agents for a fixed number of episodes, e.g., 500

Please generate **full, runnable Python code in PyTorch** implementing this, including:

- Agent class
- Reward transformations
- Environment adapter (if needed)
- Training loop
- Example initialization that works directly with this `PokerEnv`
