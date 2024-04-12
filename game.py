import pygame
from screen import Screen


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = Screen()
        self.is_game_run = True

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

            self.event_tracking()
            self.screen.update()

            # Обновление экрана (всегда в конце цикла)
            pygame.display.flip()

        pygame.quit()
