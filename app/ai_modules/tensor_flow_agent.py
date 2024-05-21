import random
from collections import deque
from typing import Tuple

from models.tensor_flow__dqn_model import DQN

MAX_MEMORY = 100_000
BATCH_SIZE = 1000


class TensorFlowAgent:

    def __init__(self, input_shape: Tuple[int, int]):
        self.n_games = 0
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = DQN(input_shape)
        self.model.load()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.model.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, next_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.model.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        return self.model.get_action(state)

    def get_state(self, game):
        return game.field.get_matrix()
