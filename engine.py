from abc import abstractmethod, ABC
import pygame as pg
from geometry.vector import Vector
from config import ButtonSettings as bs
from config import PlayerSettings as ps
# TODO: перенести логику передвижения вне отрисовки

class IRendered(ABC):
    @abstractmethod
    def draw(
        self, screen_surface: pg.Surface, convert_position, zoomLevel: float
    ) -> None:
        """convert_position - функция для преобразования позиции объекта в его позицию на экране"""
        pass

    @abstractmethod
    def set_position(self, new_position: Vector):
        pass


class IPhysics(ABC):
    @abstractmethod
    def update(self, entities: list["IPhysics"]) -> None:
        pass


class RenderedRect(pg.sprite.Sprite, IRendered):
    def __init__(self, position: Vector, size: Vector, color: tuple[int]):
        super().__init__()
        self.size = size
        self.color = color
        self.position = position
        self.rect = pg.Rect(*position.pair(), *size.pair())

    def draw(self, screen_surface: pg.Surface, convert_position, zoomLevel: float):
        size = self.size * zoomLevel
        self.rect.centerx = int(self.position.x)
        self.rect.centery = int(self.position.y)
        new_position: Vector = convert_position(self.position)
        pg.draw.rect(
            screen_surface, self.color, pg.Rect(*new_position.pair(), *size.pair())
        )

    def set_position(self, new_position: Vector):
        self.position = new_position


class Bar(IRendered):
    """Шкала здоровья/маны и прочего"""

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

    def draw(self, screen_surface: pg.Surface, convert_position, zoomLevel: float):
        self.percent = max(0, min(self.percent, 1))

        self.bg_bar.position = self.position
        self.movable_bar.position = self.position + self.ident
        self.movable_bar.size.x = self.percent * (self.bg_bar.size.x - 2 * self.ident.x)

        self.bg_bar.draw(screen_surface, convert_position, zoomLevel)
        self.movable_bar.draw(screen_surface, convert_position, zoomLevel)

    def set_position(self, new_position: Vector):
        self.position = new_position


class RasterEntity(pg.sprite.Sprite, IRendered):
    def __init__(self, image_path: str) -> None:
        super().__init__()
        self.image = pg.image.load(image_path)
        self.position = Vector(0, 0)
        self.rect = self.image.get_rect()
        self.size = Vector(self.rect.w, self.rect.h)

    def draw(self, screen_surface: pg.Surface, convert_position, zoomLevel: float):
        size = self.size * zoomLevel
        self.rect.centerx = int(self.position.x)
        self.rect.centery = int(self.position.y)
        new_position: Vector = convert_position(self.position)
        image = pg.transform.scale(self.image, size.pair())
        screen_surface.blit(image, new_position.pair())

    def set_position(self, new_position: Vector):
        self.position = new_position


class Actor(RasterEntity, IPhysics):
    def __init__(self, image_path: str) -> None:
        super().__init__(image_path)
        self.move_direction = Vector(0, 0)  # задаёт только направление
        self.speed = ps.speed

    def update(self, entities: list["IPhysics"]) -> None:
        delta_position = self.move_direction.get_normalization() * self.speed
        self.position += delta_position
        for entity in entities:
            if self == entity:
                continue
            if pg.sprite.collide_rect(self, entity):
                print(entity.position)
                self.position -= 2*delta_position


class Player(Actor):
    def event_tracking(self, event: pg.event.Event):
        if event.type == pg.KEYDOWN or event.type == pg.KEYUP:
            if event.key in bs.move_buttons.values():
                direct = 1 if (event.type == pg.KEYDOWN) else -1
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

    def __init__(self, rect: pg.Rect, zoomLevel=1.0) -> None:
        self.rect = rect
        self.zoomLevel = zoomLevel
        self.world_position = Vector(0.0, 0.0)

        self.speed = 0.0
        self.trackedEntity: IRendered = None

    def set_tracked_entity(self, entity: IRendered, speed=0.0):
        assert 0 <= speed <= 1
        self.speed = speed
        self.trackedEntity = entity

    def render(self, screen_surface: pg.Surface, entities: list[IRendered]) -> None:
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

    def set_zoom(self, new_zoom_level: float):
        self.zoomLevel = new_zoom_level


class Layer:
    """Контейнер для сущностей и камеры отображаемой их"""

    def __init__(self, camera: Camera, z_index: int = 1) -> None:
        self.z_index = z_index
        self.camera = camera
        self.display_entities: list[IRendered] = []

    def render(self, screen_surface: pg.Surface) -> None:
        self.camera.render(screen_surface, self.display_entities)

    def set_tracked_entity(self, entity: IRendered, speed=0.0):
        self.camera.set_tracked_entity(entity, speed)

    def add_entity(self, entity: IRendered):
        self.display_entities.append(entity)

    def add_entities(self, entities: list[IRendered]):
        self.display_entities += entities

    def set_zoom(self, new_zoom_level: float):
        self.camera.set_zoom(new_zoom_level)


class Screen:
    """Набор слоёв"""

    def __init__(self, surface: pg.Surface) -> None:
        self.surface = surface
        self.layers: dict[str, Layer] = {}
        self.sorted_layers: list[str] = []

    def add_layer(self, l_name: str, display_area: pg.Rect, z_index: int = 1):
        self.layers[l_name] = Layer(Camera(display_area), z_index)
        self.sorted_layers = list(
            zip(*sorted(self.layers.items(), key=lambda it: it[1].z_index))
        )[0]

    def add_entity_on_layer(self, l_name: str, entity: IRendered):
        self.layers[l_name].add_entity(entity)

    def add_entities_on_layer(self, l_name: str, entities: list[IRendered]):
        self.layers[l_name].add_entities(entities)

    def set_tracked_entity(self, l_name: str, entity: IRendered, speed=0.0):
        self.layers[l_name].set_tracked_entity(entity, speed)

    def render(self) -> None:
        for l_name in self.sorted_layers:
            self.layers[l_name].render(self.surface)

    def get_entities(self, l_name: str):
        return self.layers[l_name].display_entities

    @abstractmethod
    def event_tracking(self, event: pg.event.Event):
        pass

    @abstractmethod
    def update(self):
        pass
