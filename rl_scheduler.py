import random
from typing import List
from config import Config

class QLearningScheduler:
    """
    A basic Q-learning scheduler for discrete decisions (e.g., posting times).
    """
    def __init__(self, alpha=Config.Q_ALPHA, gamma=Config.Q_GAMMA):
        self.alpha = alpha
        self.gamma = gamma
        self.Q = {}  # Dictionary keyed by (state, action)

    def get_Q(self, state, action) -> float:
        return self.Q.get((state, action), 0.0)

    def set_Q(self, state, action, value: float):
        self.Q[(state, action)] = value

    def choose_action(self, state, possible_actions: List[str]) -> str:
        """
        Uses an epsilon-greedy policy to choose an action.
        """
        epsilon = 0.1
        if random.random() < epsilon:
            return random.choice(possible_actions)
        action_values = [(a, self.get_Q(state, a)) for a in possible_actions]
        best_action = max(action_values, key=lambda x: x[1])[0]
        return best_action

    def update(self, state, action, reward: float, next_state, possible_next_actions: List[str]):
        """
        Updates Q-values using the Q-learning formula.
        """
        old_val = self.get_Q(state, action)
        max_next = max([self.get_Q(next_state, a) for a in possible_next_actions]) if possible_next_actions else 0.0
        new_val = old_val + self.alpha * (reward + self.gamma * max_next - old_val)
        self.set_Q(state, action, new_val)
