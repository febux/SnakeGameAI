import pygame

from app.app import App, Direction, AppLoop
from constants.colors import Color


class AppAI(App):

    def start_game(self):
        super(AppAI, self).start_game()
        self.direction = self.changeto = Direction.RIGHT

    def game_over(self) -> None:
        self.direction = self.changeto = Direction.UNKNOWN
        self.app_loop = AppLoop.STOP
        gaOFont = pygame.font.SysFont('Garamond', self.font_size * 2)
        self.game_over_surface = gaOFont.render('Game Over! '
                                                'Press R to start again', True, Color.RED.value)
        gaORectangular = self.game_over_surface.get_rect()
        gaORectangular.midtop = (int(self.app_height / 2), int(self.app_width / 3))
        self.playSurface.blit(self.game_over_surface, gaORectangular)
        pygame.display.update()

    def run(self):
        while True:
            self.event_listener()

            if self.app_loop is AppLoop.RUN:
                self.check_self_bait()

                self.check_border_cross()

                self.change_position()

                self.monitoring_food_bait()

                self.draw_snake()

                self.draw_food()

                self.show_score()
            else:
                self.game_over()

            pygame.display.update()

            self.fpsController.tick(self.speed)
