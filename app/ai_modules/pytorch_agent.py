import random
from collections import deque
from typing import List
import torch

from app.app import Direction, App
from field.cells import Head
from models.py_torch__model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000


class PyTorchAgent:

    def __init__(self, *, food_multiplier: int = 1, train: bool = False):
        self.n_games = 0
        self.epsilon = 80 if train else -1  # randomness first epsilon games
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(7 + (4 * food_multiplier), 256, 128, 3)
        self.model.load()
        self.trainer = QTrainer(self.model, lr=0.001, gamma=self.gamma)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, next_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        epsilon = self.epsilon - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            prediction = self.model(torch.tensor(state, dtype=torch.float))
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def get_state(self, game: App) -> List[int]:
        head = game.field.snake.head
        point_l = Head(loc_x=head.loc_x - game.block_size, loc_y=head.loc_y)
        point_r = Head(loc_x=head.loc_x + game.block_size, loc_y=head.loc_y)
        point_u = Head(loc_x=head.loc_x, loc_y=head.loc_y - game.block_size)
        point_d = Head(loc_x=head.loc_x, loc_y=head.loc_y + game.block_size)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
        ]

        for food in game.field.food:
            state += [
                # Food location
                food.loc_x < head.loc_x,  # food left
                food.loc_x > head.loc_x,  # food right
                food.loc_y < head.loc_y,  # food up
                food.loc_y > head.loc_y  # food down
            ]
        return list(map(int, state))
