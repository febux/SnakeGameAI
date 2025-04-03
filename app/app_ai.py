import numpy as np
import pygame

from app.ai_modules.pytorch_agent import PyTorchAgent
from app.ai_modules.plot import plot
from app.app import App, Direction
from constants.colors import Color
from logger import self_logger


class AppAI(App):

    def __init__(
        self,
        app_height: int = 600,
        app_width: int = 400,
        *,
        block_size: int = 10,
        food_multiplier: int = 1,
        speed: int = 5,
        plot_available: bool = False,
        train: bool = False,
    ) -> None:
        super(AppAI, self).__init__(
            app_height=app_height,
            app_width=app_width,
            block_size=block_size,
            food_multiplier=food_multiplier,
            speed=speed,
        )
        self.agent = PyTorchAgent(food_multiplier=food_multiplier, train=train)
        self.train = train
        self.plot_available = plot_available
        self.frame_iteration = 0
        self.REWARD_VALUE = 10
        self.FRAME_ITERATION = 200

    def start_game(self):
        super(AppAI, self).start_game()
        self.direction = self.changeto = Direction.RIGHT
        self.frame_iteration = 0

    def game_over(self) -> None:
        self.direction = self.changeto = Direction.UNKNOWN

    def change_position(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.changeto = new_dir

    def monitoring_food_bait(self, agent_reward = 0):
        for index, food in enumerate(self.field.food):
            if self.field.snake.head.loc_x == food.loc_x and self.field.snake.head.loc_y == food.loc_y:
                self.eat_food(index)
                self.score += 1
                agent_reward += self.REWARD_VALUE
                self.increase_body()
                self.add_food()
        if self.direction != Direction.UNKNOWN and self.changeto != Direction.UNKNOWN:
            self.field.snake.body.cells.pop()

        return agent_reward

    def check_frame_iteration(self):
        if self.frame_iteration > self.FRAME_ITERATION * len(self.field.snake.body.cells):
            return True
        return False

    def check_useless_walking(self):
        if self.frame_iteration > self.FRAME_ITERATION * len(self.field.snake.body.cells) / 2 and self.score == 0:
            return True
        return False

    def game_step(self):
        self.move()
        agent_reward = 0

        if self.is_collision() or self.check_frame_iteration():
            agent_reward -= self.REWARD_VALUE
            self.game_over()
            return agent_reward, True
        elif self.check_useless_walking():
            agent_reward -= self.REWARD_VALUE
        else:
            agent_reward = self.monitoring_food_bait(agent_reward)
            self.playSurface.fill(Color.WHITE.value)
            self.draw_snake()
            self.draw_food()
            self.show_score()

        pygame.display.update()
        self.fpsController.tick(self.speed)

        return agent_reward, False

    def run(self):
        plot_scores = []
        plot_mean_scores = []
        total_score = 0
        record = 0

        while True:
            self.event_listener()
            # get old state
            self.frame_iteration += 1
            state_old = self.agent.get_state(self)
            # get move
            final_move = self.agent.get_action(state_old)
            # perform move and get new state
            self.change_position(final_move)
            reward, game_over = self.game_step()
            state_new = self.agent.get_state(self)

            if self.train:
                # train short memory
                self.agent.train_short_memory(state_old, final_move, reward, state_new, game_over)
                # remember
                self.agent.remember(state_old, final_move, reward, state_new, game_over)

            if game_over:
                # train long memory, plot result
                self.agent.n_games += 1

                if self.train:
                    self.agent.train_long_memory()

                    if self.score > record:
                        record = self.score
                        self.agent.model.save()

                self_logger.info(f'Game #{self.agent.n_games} Score: {self.score} Record: {record}')

                plot_scores.append(self.score)
                total_score += self.score
                mean_score = total_score / self.agent.n_games
                plot_mean_scores.append(mean_score)
                if self.plot_available:
                    plot(plot_scores, plot_mean_scores)
                self.start_game()
