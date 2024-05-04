import numpy as np
import tensorflow as tf


class DQN:
    def __init__(self, game):
        self.game = game
        self.model = self.create_model()
        self.target_model = self.create_model()
        self.update_target_model()
        self.optimizer = tf.keras.optimizers.RMSprop(learning_rate=0.00025)
        self.discount = 0.95
        self.exploration_rate = 1.0
        self.exploration_rate_decay = 0.995
        self.min_exploration_rate = 0.01
        self.batch_size = 32
        self.train_step_counter = 0

    def create_model(self):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(self.game.height, self.game.width, 1)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dense(3, activation='linear')
        ])
        model.compile(loss=tf.keras.losses.MSE, optimizer=self.optimizer)
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def get_action(self, state):
        if np.random.random() < self.exploration_rate:
            return np.random.randint(0, 3)
        state = np.array([state])
        action_values = self.model.predict(state)
        return np.argmax(action_values[0])

    def train(self):
        if self.train_step_counter % self.batch_size == 0:
            minibatch = []
            for _ in range(self.batch_size):
                # Choose a random mini-batch of experiences
                index = np.random.randint(0, len(self.game_memory))
                experience = self.game_memory[index]

                # Update the target model
                self.update_target_model()

                # Get the expected Q-value for the current state and the chosen action
                current_state, action, reward, next_state, done = experience
                expected_q_value = reward
                if not done:
                    expected_q_value += self.discount * np.amax(self.target_model.predict(np.array([next_state])))

                # Get the current Q-value for the current state and all actions
                current_state_values = self.model.predict(np.array([current_state]))
                current_q_value = current_state_values[0][action]

                # Calculate the loss
                loss = tf.keras.losses.MSE(expected_q_value, current_q_value)

                # Backpropagate the loss
                self.optimizer.minimize(loss, self.model.trainable_weights)

                # Save the experience to the minibatch
                minibatch.append(experience)

            # Update the game memory with the experiences in the minibatch
            self.game_memory = minibatch
            self.train_step_counter = 0

    def save(self, filename):
        self.model.save(filename)

    def load(self, filename):
        self.model = tf.keras.models.load_model(filename)
