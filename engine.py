from abc import abstractmethod, ABC
import pygame
from geometry.vector import Vector
from config import ButtonSettings as bs
from config import PlayerSettings as ps


class IEntity(ABC):
    @abstractmethod
    def draw(
        self, screen_surface: pygame.Surface, convert_position, zoomLevel: float
    ) -> None:
        pass

    @abstractmethod
    def update(self, entities: list["IEntity"]) -> None:
        pass


class RenderedRect(pygame.sprite.Sprite, IEntity):
    def __init__(self, position: Vector, size: Vector, color: tuple[int]):
        super().__init__()
        self.size = size
        self.color = color
        self.position = position
        self.rect = pygame.Rect(*position.pair(), *size.pair())

    def update(self, entities: list[IEntity]):
        self.rect.centerx = int(self.position.x)
        self.rect.centery = int(self.position.y)

    def draw(self, screen_surface: pygame.Surface, convert_position, zoomLevel: float):
        size = self.size * zoomLevel
        new_position: Vector = convert_position(self.position)
        pygame.draw.rect(
            screen_surface, self.color, pygame.Rect(*new_position.pair(), *size.pair())
        )


class Bar(IEntity):
    def __init__(
        self, position: Vector, size: Vector, color: tuple[int], bg_color: tuple[int]
    ):
        self.percent = 1
        self.position = position
        self.bg_bar = RenderedRect(position, size, bg_color)
        self.ident = Vector(size.y * 0.1, size.y * 0.1)
        self.movable_bar = RenderedRect(
            position + self.ident, size - 2 * self.ident, color
        )

    def update(self, entities: list[IEntity]):
        self.percent = max(0, min(self.percent, 1))

        self.bg_bar.position = self.position
        self.bg_bar.update(entities)

        self.movable_bar.position = self.position + self.ident
        self.movable_bar.size.x = self.percent * (self.bg_bar.size.x - 2 * self.ident.x)
        self.movable_bar.update(entities)

    def draw(self, screen_surface: pygame.Surface, convert_position, zoomLevel: float):
        self.bg_bar.draw(screen_surface, convert_position, zoomLevel)
        self.movable_bar.draw(screen_surface, convert_position, zoomLevel)


class RasterEntity(pygame.sprite.Sprite, IEntity):
    def __init__(self, image_path: str) -> None:
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.position = Vector(0, 0)
        self.rect = self.image.get_rect()
        self.size = Vector(self.rect.w, self.rect.h)

    def update(self, entities: list[IEntity]):
        self.rect.centerx = int(self.position.x)
        self.rect.centery = int(self.position.y)

    def draw(self, screen_surface: pygame.Surface, convert_position, zoomLevel: float):
        size = self.size * zoomLevel
        new_position: Vector = convert_position(self.position)
        image = pygame.transform.scale(self.image, size.pair())
        screen_surface.blit(image, new_position.pair())


class Actor(RasterEntity):
    def __init__(self, image_path: str) -> None:
        super().__init__(image_path)
        self.move_direction = Vector(0, 0)  # может содержать только -1, 0, 1.
        self.speed = ps.speed

    def move(self, entities: list[RasterEntity]):
        self.position += self.move_direction.get_normalization() * self.speed

    def update(self, entities: list[RasterEntity]):
        self.move(entities)
        super().update(entities)


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


class Camera:
    """
    Класс обладающий областью видимости, который при помощи методов отображет объекты в ней.\\
    При помощи метода set_tracked_entity, можно прикрепить камеру к сущности и следить за ней.
    """

    def __init__(self, rect: pygame.Rect, zoomLevel=1.0) -> None:
        self.rect = rect
        self.zoomLevel = zoomLevel
        self.world_position = Vector(0.0, 0.0)

        self.speed = 0.0
        self.trackedEntity: IEntity = None

    def set_tracked_entity(self, entity: IEntity, speed=0.0):
        assert 0 <= speed <= 1
        self.speed = speed
        self.trackedEntity = entity

    def render(self, screen_surface: pygame.Surface, entities: list[IEntity]) -> None:
        position_on_camera = lambda position: position
        if self.trackedEntity is not None:
            a = self.speed
            entity = self.trackedEntity
            position = Vector(self.rect.x, self.rect.y)
            size = Vector(self.rect.width, self.rect.height)

            target_position = entity.position + 0.5 * entity.size
            self.world_position = self.world_position * (1 - a) + target_position * a
            offset = position + 0.5 * size - (self.zoomLevel * self.world_position)
            position_on_camera = lambda position: (self.zoomLevel * position) + offset

        # START render
        screen_surface.set_clip(self.rect)

        # render entities
        for e in entities:
            e.draw(screen_surface, position_on_camera, self.zoomLevel)

        # FINISH render
        screen_surface.set_clip(None)


class Layer:
    def __init__(self, camera: Camera, z_index: int = 1) -> None:
        self.z_index = z_index
        self.camera = camera
        self.display_entities: list[IEntity] = []

    def render(self, screen_surface: pygame.Surface) -> None:
        self.camera.render(screen_surface, self.display_entities)


class Screen:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        self.layers: dict[str, Layer] = {}
        self.sorted_layers: list[str] = []

    def add_layer(self, l_name: str, display_area: pygame.Rect, z_index: int = 1):
        self.layers[l_name] = Layer(Camera(display_area), z_index)
        self.sorted_layers = list(
            zip(*sorted(self.layers.items(), key=lambda it: it[1].z_index))
        )[0]

    def add_entity_on_layer(self, l_name: str, entity: IEntity):
        self.layers[l_name].display_entities.append(entity)

    def add_entities_on_layer(self, l_name: str, entities: IEntity):
        self.layers[l_name].display_entities += entities

    def render(self) -> None:
        for l_name in self.sorted_layers:
            self.layers[l_name].render(self.surface)
