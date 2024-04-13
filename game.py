import pygame
from screen import Screen
from config import ScreenSettings


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.main_surface = Screen()
        self.is_game_run = True
        self.FPS_clock = pygame.time.Clock()

    def event_tracking(self):
        """Отслеживание событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # событие: "закрыть окно"
                self.is_game_run = False

    def run(self) -> None:
        """Запуск игры"""
        # Цикл игры
        while self.is_game_run:
            self.FPS_clock.tick(ScreenSettings.FPS)

            self.event_tracking()
            self.main_surface.update()

            # Обновление экрана (всегда в конце цикла)
            pygame.display.flip()

        pygame.quit()
