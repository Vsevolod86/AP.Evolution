import pygame

from engine import Actor, Bar, Player, RenderedRect, Screen
from config import ScreenSettings as ss
from config import Colors as crl
from geometry.vector import Vector


class GameScreen(Screen):
    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        # ADD background
        w, h, i = surface.get_width(), surface.get_height(), 5
        self.add_layer("bg", pygame.Rect(i, i, w - 2 * i, h - 2 * i))
        bg = RenderedRect(Vector(i, i), Vector(w, h), ss.bg_color)
        self.add_entity_on_layer("bg", bg)

        # ADD map
        self.add_layer("map", pygame.Rect(i, i, w - 2 * i, h - 2 * i))

        self.player = Player("images/bacteria.png")
        self.add_entity_on_layer("map", self.player)
        self.set_tracked_entity("map", self.player, ss.camera_speed)

        enemy = Actor("images/bacteria.png")
        enemy.position = Vector(90, 20)
        self.add_entity_on_layer("map", enemy)

        rect = RenderedRect(Vector(30, 70), Vector(30, 10), ss.bg_color)
        rect.position = Vector(100, 100)
        self.add_entity_on_layer("map", rect)

        # ADD interface
        self.add_layer("interface", pygame.Rect(i, i, w - 2 * i, h - 2 * i))

        barHP = Bar(Vector(30, 30), Vector(50, 10), crl.green, crl.silver)
        barHP.percent = 0.8
        self.add_entity_on_layer("interface", barHP)

    def event_tracking(self, event: pygame.event.Event):
        """Отслеживание событий"""
        self.player.event_tracking(event)

    def update(self):
        self.player.update(self.get_entities("map"))


class Game:
    def __init__(self) -> None:
        pygame.init()
        # Окно игры: размер, позиция
        self.surface = pygame.display.set_mode((ss.width, ss.height))
        pygame.display.set_caption(ss.game_title)
        self.FPS_clock = pygame.time.Clock()

        self.is_game_run = True
        self.game_screen = GameScreen(self.surface)

    def event_tracking(self):
        """Отслеживание событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_game_run = False  # "закрыть игру"
            elif self.is_game_run:
                self.game_screen.event_tracking(event)

    def run(self) -> None:
        """Запуск игры"""

        # Цикл игры
        while self.is_game_run:
            self.FPS_clock.tick(ss.FPS)
            self.event_tracking()

            self.game_screen.update()

            self.surface.fill(crl.pink)
            self.game_screen.render()

            # Обновление экрана (всегда в конце цикла)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
