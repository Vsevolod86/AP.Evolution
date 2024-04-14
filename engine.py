from abc import abstractmethod, ABC
import pygame
from geometry.vector import Vector
from config import ButtonSettings as bs
from config import ScreenSettings as ss
from config import PlayerSettings as ps


class IRenderable(ABC):
    @abstractmethod
    def update(
        self, screen_surface: pygame.Surface, entities: list["RasterEntity"]
    ) -> None:
        pass

    @abstractmethod
    def draw(
        self, screen_surface: pygame.Surface, position: Vector, zoomLevel: float
    ) -> None:
        pass


class VectorEntity(pygame.sprite.Sprite, IRenderable):
    def __init__(self, position: Vector, size: Vector, color: tuple[int]):
        super().__init__()
        self.position = position
        self.rect = pygame.Rect(*position.pair(), *size.pair())
        self.size = size
        self.color = color

    def update(self, screen_surface: pygame.Surface, entities: list["RasterEntity"]):
        self.rect.centerx = int(self.position.x)
        self.rect.centery = int(self.position.y)

    def draw(self, screen_surface: pygame.Surface, position: Vector, zoomLevel: float):
        size = self.size * zoomLevel
        pygame.draw.rect(
            screen_surface, (0, 0, 128), pygame.Rect(*position.pair(), *size.pair())
        )


class RasterEntity(pygame.sprite.Sprite, IRenderable):
    def __init__(self, image_path: str) -> None:
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.position = Vector(0, 0)
        self.rect = self.image.get_rect()
        self.size = Vector(self.rect.w, self.rect.h)

    def update(self, screen_surface: pygame.Surface, entities: list["RasterEntity"]):
        self.rect.centerx = int(self.position.x)
        self.rect.centery = int(self.position.y)

    def draw(self, screen_surface: pygame.Surface, position: Vector, zoomLevel: float):
        size = self.size * zoomLevel
        image = pygame.transform.scale(self.image, size.pair())
        screen_surface.blit(image, position.pair())


class Actor(RasterEntity):
    def __init__(self, image_path: str) -> None:
        super().__init__(image_path)
        self.move_direction = Vector(0, 0)  # может содержать только -1, 0, 1.
        self.speed = ps.speed

    def move(self, entities: list[RasterEntity]):
        self.position += self.move_direction.get_normalization() * self.speed

    def update(self, screen_surface: pygame.Surface, entities: list[RasterEntity]):
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

#TODO: переделать классы ниже
# в класс screen сделать три камеры (фон, персонажи, display)
class Camera:
    def __init__(
        self,
        position: Vector,
        size: Vector,
        speed=0.0,
        zoomLevel=1.0,
        entity: IRenderable = None,
    ) -> None:
        assert 0 <= speed <= 1
        self.position = position
        self.size = size
        self.rect = pygame.Rect(*self.position.pair(), *self.size.pair())

        self.speed = speed
        self.zoomLevel = zoomLevel
        self.world_position = Vector(0.0, 0.0)

        self.trackedEntity = entity

    def _render(
        self,
        screen_surface: pygame.Surface,
        entities: list[IRenderable],
        new_position,
        is_fill_bg: bool,
    ) -> None:
        screen_surface.set_clip(self.rect)  # START render

        # fill camera background
        if is_fill_bg:
            screen_surface.fill(ss.bg_color)

        # render entities
        for e in entities:
            e.draw(screen_surface, new_position(e), self.zoomLevel)

        screen_surface.set_clip(None)  # FINISH render

    def update_rendered(
        self, screen_surface: pygame.Surface, entities: list[IRenderable]
    ) -> None:
        # update camera (наблюдение за персонажем)
        if self.trackedEntity is not None:
            target_position = (
                self.trackedEntity.position + 0.5 * self.trackedEntity.size
            )
            self.world_position = (
                self.world_position * (1 - self.speed) + target_position * self.speed
            )
        offset = (
            self.position + 0.5 * self.size - (self.zoomLevel * self.world_position)
        )
        self._render(
            screen_surface,
            entities,
            lambda e: (self.zoomLevel * e.position) + offset,
            True,
        )

    def update_display(
        self, screen_surface: pygame.Surface, entities: list[IRenderable]
    ) -> None:
        self._render(screen_surface, entities, lambda e: e.position, False)


class Screen:
    def __init__(self, camera: Camera) -> None:
        self.rendered_entities: list[IRenderable] = []
        self.display_entities: list[IRenderable] = []
        self.camera = camera

    def add_rendered_entities(self, entities) -> None:
        self.rendered_entities += entities

    def add_display_entities(self, entities) -> None:
        self.display_entities += entities

    def update(self, screen_surface: pygame.Surface) -> None:
        self.camera.update_rendered(screen_surface, self.rendered_entities)
        self.camera.update_display(screen_surface, self.display_entities)


class GameScreen(Screen):
    def __init__(self, camera: Camera) -> None:
        super().__init__(camera)
        pass


class Game:
    def __init__(self) -> None:
        pygame.init()
        # Окно игры: размер, позиция
        self.surface = pygame.display.set_mode((ss.width, ss.height))
        pygame.display.set_caption(ss.game_title)

        self.FPS_clock = pygame.time.Clock()

        self.is_game_run = True
        self.player: Player = None
        self.entities: list[IRenderable] = []

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
        self.entities[1].position = Vector(100, 100)

        self.camera = Camera(
            Vector(10, 10),
            Vector(ss.width - 100, ss.height - 100),
            ss.camera_speed,
            ss.camera_zoom,
            self.player,
        )
        # Цикл игры
        while self.is_game_run:
            self.FPS_clock.tick(ss.FPS)
            self.event_tracking()

            for entity in self.entities:
                entity.update(self.surface, self.entities)

            self.surface.fill(ss.black)
            self.camera.update_rendered(self.surface, self.entities)
            # self.camera.update_display(self.surface, self.entities)

            # Обновление экрана (всегда в конце цикла)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
