# from abc import abstractmethod
import pygame
from geometry.vector import Vector
from config import ButtonSettings as bs
from config import ScreenSettings as ss


class Entity(pygame.sprite.Sprite):
    def __init__(self, image_path: str) -> None:
        super(Entity, self).__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.position = Vector(0, 0)

    def update(self, screen_surface: pygame.Surface, entities: list["Entity"]):
        self.rect.centerx = int(self.position.x)
        self.rect.centery = int(self.position.y)

    def draw(self, screen_surface: pygame.Surface):
        screen_surface.blit(self.image, self.rect)


class Actor(Entity):
    def __init__(self, image_path: str) -> None:
        super().__init__(image_path)
        self.move_direction = Vector(0, 0)  # может содержать только -1, 0, 1.

    def move(self, entities: list[Entity]):
        self.position += self.move_direction.get_normalization()

    def update(self, screen_surface: pygame.Surface, entities: list[Entity]):
        self.move(entities)
        super().update(screen_surface, entities)


class Player(Actor):
    def event_tracking(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.key in bs.move_buttons.values():
                direct = 1 if (event.type == pygame.KEYDOWN) else -1
                if event.key == bs.move_buttons["right"]:
                    self.move_direction.x += direct
                elif event.key == bs.move_buttons["left"]:
                    self.move_direction.x -= direct
                elif event.key == bs.move_buttons["up"]:
                    self.move_direction.y -= direct
                elif event.key == bs.move_buttons["down"]:
                    self.move_direction.y += direct
                self.move_direction = self.move_direction.sign()


class Game:
    def __init__(self) -> None:
        pygame.init()
        # Окно игры: размер, позиция
        self.surface = pygame.display.set_mode((ss.width, ss.height))
        pygame.display.set_caption(ss.game_title)
        self.surface.fill(ss.bg_color)

        self.FPS_clock = pygame.time.Clock()

        self.is_game_run = True
        self.player: Player = None

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
        # Цикл игры
        while self.is_game_run:
            self.FPS_clock.tick(ss.FPS)
            self.event_tracking()

            self.surface.fill(ss.bg_color)
            self.player.update(self.surface, [])

            self.player.draw(self.surface)

            # Обновление экрана (всегда в конце цикла)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
