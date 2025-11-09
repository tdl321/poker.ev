import torch
import torch.optim as optim
import numpy as np
import sys
from poker_agent import PokerAgent
from poker_env_adapter import PokerEnvAdapter, risk_averse_reward, risk_neutral_reward, risk_seeking_reward


class MultiAgentPokerTrainer:
    """
    Multi-agent poker trainer using policy gradient methods.

    Trains multiple agents with different risk profiles to compete against each other.
    """

    def __init__(self, num_players, endowment, state_dim, hidden_dim=128, lr=0.001, small_blind=10, big_blind=20):
        """
        Initialize the trainer.

        Args:
            num_players: Number of players/agents
            endowment: Starting chips for each player
            state_dim: Dimension of state vector
            hidden_dim: Hidden layer size for agents
            lr: Learning rate
            small_blind: Small blind amount
            big_blind: Big blind amount
        """
        self.num_players = num_players
        self.endowment = endowment
        self.state_dim = state_dim
        self.hidden_dim = hidden_dim
        self.lr = lr

        # Create environment
        self.env = PokerEnvAdapter(num_players, endowment, small_blind, big_blind)

        # Create agents with different risk profiles
        self.agents = []
        self.optimizers = []
        self.risk_functions = []

        # Distribute risk profiles among agents
        risk_profiles = ['neutral', 'averse', 'seeking']
        risk_funcs = [risk_neutral_reward, risk_averse_reward, risk_seeking_reward]

        for i in range(num_players):
            profile_idx = i % len(risk_profiles)
            agent = PokerAgent(state_dim, hidden_dim, risk_profile=risk_profiles[profile_idx])
            optimizer = optim.Adam(agent.parameters(), lr=lr)

            self.agents.append(agent)
            self.optimizers.append(optimizer)
            self.risk_functions.append(risk_funcs[profile_idx])

        # Training statistics
        self.episode_rewards = [[] for _ in range(num_players)]
        self.episode_lengths = []

    def play_episode(self):
        """
        Play one complete poker hand (episode).

        Returns:
            episode_data: List of (states, actions, raise_amounts) for each player
            final_rewards: Final rewards for all players
        """
        # Reset environment
        states = self.env.reset()

        # Storage for episode data (don't store logits, we'll recompute them)
        episode_data = [{'states': [], 'actions': [], 'raise_amounts': []}
                        for _ in range(self.num_players)]

        # Play through all betting rounds
        for round_name in ["Pre-Flop", "Flop", "Turn", "River"]:
            # Advance to next round (except for pre-flop)
            if round_name != "Pre-Flop":
                states, done = self.env.advance_round()
                if done:
                    break

            # Betting round
            while not self.env.is_round_done():
                # Get active players who need to act
                for player_id in range(self.num_players):
                    # Check if player needs to act
                    if (self.env.env.active_players[player_id] and
                        not self.env.env.played[player_id] and
                        self.env.env.money[player_id] > 0):

                        # Get current state
                        state = self.env.env.get_state(player_id)

                        # Agent selects action
                        action, raise_amount, _, _ = self.agents[player_id].act(
                            state, self.env.env, player_id
                        )

                        # Store data
                        episode_data[player_id]['states'].append(state)
                        episode_data[player_id]['actions'].append(action)
                        episode_data[player_id]['raise_amounts'].append(raise_amount)

                        # Execute action
                        next_state, reward, done = self.env.step(player_id, action, raise_amount)

                        if done:
                            break

                if self.env.env.game_over:
                    break

            if self.env.env.game_over:
                break

        # Showdown - get final rewards
        final_rewards = self.env.showdown()

        return episode_data, final_rewards

    def compute_returns(self, final_rewards):
        """
        Compute returns for each player using their risk function.

        Args:
            final_rewards: List of final rewards for all players

        Returns:
            transformed_rewards: List of transformed rewards
        """
        transformed_rewards = []
        for i, reward in enumerate(final_rewards):
            transformed = self.risk_functions[i](reward)
            transformed_rewards.append(transformed)
        return transformed_rewards

    def update_agents(self, episode_data, returns):
        """
        Update agent parameters using policy gradient.

        Args:
            episode_data: List of episode data for each agent
            returns: List of returns for each agent
        """
        for player_id in range(self.num_players):
            data = episode_data[player_id]

            # Skip if no actions were taken
            if len(data['actions']) == 0:
                continue

            # Recompute forward pass to get gradients
            states_tensor = torch.stack([torch.FloatTensor(s) for s in data['states']])
            actions_tensor = torch.LongTensor(data['actions'])
            returns_tensor = torch.FloatTensor([returns[player_id]] * len(data['actions']))

            # Forward pass through agent (this time with gradients)
            action_logits, raise_logits, values = self.agents[player_id](states_tensor)

            # Compute policy loss
            # Use log probability of taken actions weighted by return
            log_probs = torch.nn.functional.log_softmax(action_logits, dim=-1)
            selected_log_probs = log_probs[range(len(actions_tensor)), actions_tensor]

            # Policy gradient loss: -log_prob * return
            # We want to maximize return, so we minimize negative return
            policy_loss = -(selected_log_probs * returns_tensor).mean()

            # Update agent
            self.optimizers[player_id].zero_grad()
            policy_loss.backward()
            self.optimizers[player_id].step()

    def train(self, num_episodes, print_every=50, verbose=False):
        """
        Train agents for a specified number of episodes.

        Args:
            num_episodes: Number of episodes to train
            print_every: Print statistics every N episodes
            verbose: Whether to print detailed episode information
        """
        print(f"Starting training for {num_episodes} episodes...")
        print(f"Agents: {self.num_players}")
        print(f"Risk profiles: {[agent.risk_profile for agent in self.agents]}")
        print("=" * 60)

        for episode in range(num_episodes):
            # Play episode
            episode_data, final_rewards = self.play_episode()

            # Compute returns with risk transformations
            returns = self.compute_returns(final_rewards)

            # Update agents
            self.update_agents(episode_data, returns)

            # Store statistics
            for i, reward in enumerate(final_rewards):
                self.episode_rewards[i].append(reward)

            # Print progress
            if (episode + 1) % print_every == 0:
                avg_rewards = [np.mean(self.episode_rewards[i][-print_every:])
                               for i in range(self.num_players)]

                print(f"\nEpisode {episode + 1}/{num_episodes}")
                print("-" * 60)
                for i in range(self.num_players):
                    print(f"  Agent {i} ({self.agents[i].risk_profile:8s}): "
                          f"Avg Reward = {avg_rewards[i]:8.2f}, "
                          f"Last Reward = {final_rewards[i]:6.0f}")

            if verbose and (episode + 1) % print_every == 0:
                print(f"  Total hands played: {episode + 1}")
                print()

        print("\n" + "=" * 60)
        print("Training complete!")
        print("=" * 60)

        # Print final statistics
        print("\nFinal Performance (last 100 episodes):")
        print("-" * 60)
        for i in range(self.num_players):
            avg_reward = np.mean(self.episode_rewards[i][-100:])
            total_reward = sum(self.episode_rewards[i])
            print(f"  Agent {i} ({self.agents[i].risk_profile:8s}): "
                  f"Avg = {avg_reward:8.2f}, Total = {total_reward:10.0f}")

    def save_agents(self, filename_prefix="poker_agent"):
        """
        Save trained agents to files.

        Args:
            filename_prefix: Prefix for saved model files
        """
        for i, agent in enumerate(self.agents):
            filename = f"{filename_prefix}_{i}_{agent.risk_profile}.pt"
            torch.save(agent.state_dict(), filename)
            print(f"Saved agent {i} to {filename}")

    def load_agents(self, filename_prefix="poker_agent"):
        """
        Load trained agents from files.

        Args:
            filename_prefix: Prefix for saved model files
        """
        for i, agent in enumerate(self.agents):
            filename = f"{filename_prefix}_{i}_{agent.risk_profile}.pt"
            agent.load_state_dict(torch.load(filename))
            print(f"Loaded agent {i} from {filename}")


def main():
    """
    Main training script.
    """
    # Configuration
    NUM_PLAYERS = 3
    ENDOWMENT = 1000
    STATE_DIM = 44  # Fixed state size from PokerEnv.get_state()
    HIDDEN_DIM = 128
    LEARNING_RATE = 0.001
    NUM_EPISODES = 500
    SMALL_BLIND = 10
    BIG_BLIND = 20

    print("Multi-Agent Poker Neural Network Training")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Players: {NUM_PLAYERS}")
    print(f"  Endowment: {ENDOWMENT}")
    print(f"  State Dimension: {STATE_DIM}")
    print(f"  Hidden Dimension: {HIDDEN_DIM}")
    print(f"  Learning Rate: {LEARNING_RATE}")
    print(f"  Episodes: {NUM_EPISODES}")
    print(f"  Small Blind: {SMALL_BLIND}")
    print(f"  Big Blind: {BIG_BLIND}")
    print("=" * 60)
    print()

    # Create trainer
    trainer = MultiAgentPokerTrainer(
        num_players=NUM_PLAYERS,
        endowment=ENDOWMENT,
        state_dim=STATE_DIM,
        hidden_dim=HIDDEN_DIM,
        lr=LEARNING_RATE,
        small_blind=SMALL_BLIND,
        big_blind=BIG_BLIND
    )

    # Train agents
    try:
        trainer.train(num_episodes=NUM_EPISODES, print_every=50, verbose=False)

        # Save trained agents
        print("\nSaving trained agents...")
        trainer.save_agents()

    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        print("Saving current progress...")
        trainer.save_agents()

    print("\nDone!")


if __name__ == "__main__":
    main()
