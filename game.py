import pygame

from engine import Bar, Camera, IEntity, Player, RasterEntity, RenderedRect, Screen
from config import ScreenSettings as ss
from geometry.vector import Vector


class GameScreen(Screen):
    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

        # ADD background
        w, h, i = surface.get_width(), surface.get_height(), 5
        self.add_layer("bg", pygame.Rect(i, i, w - 2 * i, h - 2 * i))
        bg = RenderedRect(Vector(i, i), Vector(w, h), ss.bg_color)
        self.add_entity_on_layer("bg", bg)

        i *= 10
        self.add_layer("bg2", pygame.Rect(i, i, w - 2 * i, h - 2 * i), 2)
        bg2 = RenderedRect(Vector(i, i), Vector(w, h), ss.red)
        self.add_entity_on_layer("bg2", bg2)


class Game:
    def __init__(self) -> None:
        pygame.init()
        # Окно игры: размер, позиция
        self.surface = pygame.display.set_mode((ss.width, ss.height))
        pygame.display.set_caption(ss.game_title)

        self.FPS_clock = pygame.time.Clock()

        self.is_game_run = True
        self.player: Player = None
        self.entities: list[IEntity] = []

        self.game_screen = GameScreen(self.surface)

    def event_tracking(self):
        """Отслеживание событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_game_run = False  # "закрыть игру"
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.player.event_tracking(event)

    def run(self) -> None:
        """Запуск игры"""
        self.player = Player("images/bacteria.png")
        self.entities.append(self.player)
        self.entities.append(RasterEntity("images/bacteria.png"))
        self.entities.append(RenderedRect(Vector(30, 70), Vector(30, 10), ss.bg_color))
        self.entities.append(Bar(Vector(30, 30), Vector(50, 10), ss.green, ss.red))
        self.entities[-1].percent = 0.8
        self.entities[1].position = Vector(100, 100)

        self.bg = pygame.Rect(10, 10, ss.width - 100, ss.height - 100)
        self.camera = Camera(self.bg, ss.camera_zoom)
        self.camera.set_tracked_entity(self.player, ss.camera_speed)
        # Цикл игры
        while self.is_game_run:
            self.FPS_clock.tick(ss.FPS)
            self.event_tracking()

            for entity in self.entities:
                entity.update(self.entities)

            self.surface.fill(ss.black)
            self.game_screen.render()
            self.camera.render(self.surface, self.entities)
            # self.camera.update_display(self.surface, self.entities)

            # Обновление экрана (всегда в конце цикла)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
