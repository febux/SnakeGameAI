from enum import Enum
from typing import List, Tuple

import pygame
import random
import sys
import time

from pydantic import BaseModel

from cells.body_cell import Head, Body, BodyCell
from cells.cell import Cell
from cells.food_cell import Food
from constants.colors import Color


class ShowScoreView(Enum):
    TOP_LEFT = 'TOP_LEFT'
    CENTER = 'CENTER'


class Direction(Enum):
    RIGHT = 'RIGHT'
    LEFT = 'LEFT'
    DOWN = 'DOWN'
    UP = 'UP'
    UNKNOWN = 'UNKNOWN'


class AppLoop(Enum):
    RUN = True
    STOP = False


class Field(BaseModel):
    matrix: List[List[Cell]]


class App:
    def __init__(
        self,
        app_height: int = 600,
        app_width: int = 400,
        *,
        block_size: int = 10,
        food_multiplier: int = 1,
        speed: int = 5,
    ) -> None:
        self.init_app()
        self.app_height = app_height
        self.app_width = app_width
        self.block_size = block_size
        self.speed = speed
        self.playSurface = pygame.display.set_mode((app_height, app_width))
        pygame.display.set_caption('Pythonчик')
        time.sleep(1)
        self.fpsController = pygame.time.Clock()
        self.font_size = 24 if (app_height > 500 and app_width > 300) else 14
        self.food_multiplier = food_multiplier
        self.food_array: List[Food] = []
        self.head = Head(loc_x=50, loc_y=50)
        self.body = Body(
            cells=[
                BodyCell(loc_x=80, loc_y=50),
                BodyCell(loc_x=70, loc_y=50),
                BodyCell(loc_x=60, loc_y=50)
            ],
        )
        self.food_array: List[Food] = [self.locate_food() for _ in range(self.food_multiplier)]
        self.direction = Direction.RIGHT
        self.changeto = self.direction
        self.score = 0
        self.app_loop = AppLoop.RUN
        self.game_over_surface = None

    @staticmethod
    def init_app() -> None:
        err = pygame.init()
        if err[1] == 0:
            print('Game started')
        else:
            print('Errors detected')
            sys.exit()

    def start_game(self):
        self.app_loop = AppLoop.RUN
        self.head = Head(loc_x=50, loc_y=50)
        self.body = Body(
            cells=[
                BodyCell(loc_x=80, loc_y=50),
                BodyCell(loc_x=70, loc_y=50),
                BodyCell(loc_x=60, loc_y=50)
            ],
        )
        self.food_array: List[Food] = [self.locate_food() for _ in range(self.food_multiplier)]
        self.score = 0

    @property
    def fps(self):
        return pygame.time.Clock()

    @fps.setter
    def fps(self, value):
        self.fpsController.tick(value)

    def game_over(self) -> None:
        self.app_loop = AppLoop.STOP

    def exit_game(self):
        pygame.display.update()
        gaOFont = pygame.font.SysFont('Garamond', self.font_size * 2)
        gaOSurface = gaOFont.render('Exit game', True, Color.RED.value)
        if self.game_over_surface:
            self.game_over_surface.fill(Color.WHITE.value)
            gaORectangular = self.game_over_surface.get_rect()
            gaORectangular.midtop = (int(self.app_height / 2), int(self.app_width / 3))
            self.playSurface.blit(self.game_over_surface, gaORectangular)
        gaORectangular = gaOSurface.get_rect()
        gaORectangular.midtop = (int(self.app_height / 2), int(self.app_width / 3))
        self.playSurface.blit(gaOSurface, gaORectangular)
        pygame.display.update()
        time.sleep(1)
        pygame.quit()
        sys.exit()

    def show_score(self, choice: ShowScoreView = ShowScoreView.TOP_LEFT) -> None:
        scoreFont = pygame.font.SysFont('Garamond', self.font_size)
        scoreSurface = scoreFont.render('Score: {0}'.format(self.score), True, Color.RED.value)
        scoreRectangular = scoreSurface.get_rect()
        if choice is ShowScoreView.TOP_LEFT:
            scoreRectangular.midtop = (int(self.app_height / 12), int(self.app_width / 25))
        elif choice is ShowScoreView.CENTER:
            scoreRectangular.midtop = (int(self.app_height / 2), int(self.app_width / 3))
        self.playSurface.blit(scoreSurface, scoreRectangular)
        pygame.display.flip()

    def event_listener(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_RIGHT | pygame.K_d:
                        self.changeto = Direction.RIGHT
                    case pygame.K_LEFT | pygame.K_a:
                        self.changeto = Direction.LEFT
                    case pygame.K_UP | pygame.K_w:
                        self.changeto = Direction.UP
                    case pygame.K_DOWN | pygame.K_s:
                        self.changeto = Direction.DOWN
                    case pygame.K_ESCAPE:
                        self.exit_game()
                    case pygame.K_r:
                        self.start_game()

    def change_position(self):
        if self.direction != Direction.LEFT and self.changeto == Direction.RIGHT:
            self.direction = Direction.RIGHT
        elif self.direction != Direction.RIGHT and self.changeto == Direction.LEFT:
            self.direction = Direction.LEFT
        elif self.direction != Direction.DOWN and self.changeto == Direction.UP:
            self.direction = Direction.UP
        elif self.direction != Direction.UP and self.changeto == Direction.DOWN:
            self.direction = Direction.DOWN

        match self.direction:
            case Direction.RIGHT:
                self.head.loc_x += self.block_size
            case Direction.LEFT:
                self.head.loc_x -= self.block_size
            case Direction.UP:
                self.head.loc_y -= self.block_size
            case Direction.DOWN:
                self.head.loc_y += self.block_size
            case Direction.UNKNOWN:
                pass

        if self.direction != Direction.UNKNOWN and self.changeto != Direction.UNKNOWN:
            self.body.cells.insert(0, BodyCell(loc_x=self.head.loc_x, loc_y=self.head.loc_y))

    def check_self_bait(self, head_cell: Head = None) -> bool:
        if head_cell is None:
            head_cell = self.head
        for element in self.body.cells[1:]:
            if head_cell.loc_x == element.loc_x and head_cell.loc_y == element.loc_y:
                return True
        return False

    def check_border_cross(self, head_cell: Head = None) -> bool:
        if head_cell is None:
            head_cell = self.head
        if (head_cell.loc_x > self.app_height or head_cell.loc_x < 0
                or head_cell.loc_y > self.app_width or head_cell.loc_y < 0):
            return True
        return False

    def is_collision(self, head_cell: Head = None) -> bool:
        return self.check_self_bait(head_cell) or self.check_border_cross(head_cell)

    def generate_location(self) -> Tuple[int, int]:
        return (random.randrange(1, int(self.app_height / 10)) * 10,
                random.randrange(1, int(self.app_width / 10)) * 10)

    def locate_food(self) -> Food:
        compatible_place = False
        loc_x, loc_y = self.generate_location()

        while not compatible_place:
            compatible_place = True

            for food in self.food_array:
                if loc_x == food.loc_x and loc_y == food.loc_y:
                    compatible_place = False
                    loc_x, loc_y = self.generate_location()
                    continue

            for cell in self.body.cells:
                if loc_x == cell.loc_x and loc_y == cell.loc_y:
                    compatible_place = False
                    loc_x, loc_y = self.generate_location()

        return Food(loc_x=loc_x, loc_y=loc_y)

    def draw_food(self):
        for food in self.food_array:
            pygame.draw.rect(self.playSurface, pygame.Color(*food.color),
                             pygame.Rect(food.loc_x, food.loc_y, self.block_size, self.block_size))

    def add_food(self):
        self.food_array.append(self.locate_food())

    def eat_food(self, index: int):
        self.food_array.pop(index)

    def increase_body(self):
        self.body.cells.append(BodyCell(loc_x=50, loc_y=50))

    def draw_snake(self):
        for element in self.body.cells:
            pygame.draw.rect(self.playSurface, pygame.Color(*element.color),
                             pygame.Rect(element.loc_x, element.loc_y, self.block_size, self.block_size))

    def monitoring_food_bait(self):
        for index, food in enumerate(self.food_array):
            if self.head.loc_x == food.loc_x and self.head.loc_y == food.loc_y:
                self.eat_food(index)
                self.score += 1
                self.increase_body()
                self.add_food()
        else:
            if self.direction != Direction.UNKNOWN and self.changeto != Direction.UNKNOWN:
                self.body.cells.pop()

    def game_step(self):
        if self.app_loop is AppLoop.RUN and not self.is_collision():
            self.change_position()

            self.monitoring_food_bait()

            self.playSurface.fill(Color.WHITE.value)

            self.draw_snake()

            self.draw_food()

            self.show_score()
        else:
            self.game_over()

        pygame.display.update()

        self.fpsController.tick(self.speed)

    def run(self):
        while True:
            self.event_listener()

            self.game_step()
