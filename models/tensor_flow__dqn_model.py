from typing import Tuple

import numpy as np
from keras import Sequential
from keras.src.layers import Conv2D, Flatten, Dense
from keras.src.optimizers import RMSprop
from keras.src.saving import load_model
from tensorflow.python.keras.losses import MSE


class DQN:
    def __init__(
        self,
        input_shape: Tuple[int, int],
        block_size: int,
        *,
        file_name='model.keras',
    ):
        self.input_shape = input_shape
        self.block_size = block_size
        self.model = self.create_model()
        self.target_model = self.create_model()
        self.update_target_model()
        self.optimizer = RMSprop(learning_rate=0.00025)
        self.discount = 0.95
        self.exploration_rate = 1.0
        self.exploration_rate_decay = 0.995
        self.min_exploration_rate = 0.01
        self.batch_size = 32
        self.train_step_counter = 0
        self.filename = file_name

    def create_model(self):
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(self.input_shape[0] / self.block_size, self.input_shape[1] / self.block_size, 1)),
            Conv2D(64, (3, 3), activation='relu'),
            Conv2D(64, (3, 3), activation='relu'),
            Flatten(),
            Dense(512, activation='relu'),
            Dense(3, activation='linear')
        ])
        model.compile(loss=MSE, optimizer=self.optimizer)
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def predict(self, state):
        return self.model.predict(state)

    def get_action(self, state):
        if np.random.random() < self.exploration_rate:
            return np.random.randint(0, 3)
        state = np.array([state])
        action_values = self.model.predict(state)
        return np.argmax(action_values[0])

    def train_step(self, current_state, action, reward, next_state, done):
        if self.train_step_counter % self.batch_size == 0:
            for _ in range(self.batch_size):
                # Update the target model
                self.update_target_model()

                # Get the expected Q-value for the current state and the chosen action
                expected_q_value = reward
                if not done:
                    expected_q_value += self.discount * np.amax(self.target_model.predict(np.array([next_state])))

                # Get the current Q-value for the current state and all actions
                current_state_values = self.model.predict(np.array([current_state]))
                current_q_value = current_state_values[0][action]

                # Calculate the loss
                loss = MSE(expected_q_value, current_q_value)

                # Backpropagate the loss
                self.optimizer.minimize(loss, self.model.trainable_weights)

                # Save the experience to the minibatch

            # Update the game memory with the experiences in the minibatch
            self.train_step_counter = 0

    def save(self):
        self.model.save(self.filename)

    def load(self):
        self.model = load_model(self.filename)
