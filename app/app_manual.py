import sys
import time

import pygame

from app.app import App, Direction, AppLoop
from constants.colors import Color


class AppManual(App):

    @staticmethod
    def music_on() -> None:
        pygame.mixer.init()
        pygame.mixer.music.load('../riff.mp3')
        pygame.mixer.music.play(loops=-1)

    @staticmethod
    def music_off() -> None:
        pygame.mixer.music.stop()

    def start_game(self):
        super(AppManual, self).start_game()
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
                    case pygame.K_p:
                        self.music_on()
                    case pygame.K_m:
                        self.music_off()

    def run(self):
        while True:
            self.event_listener()
            self.game_step()
