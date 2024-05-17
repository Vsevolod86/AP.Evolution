from abc import abstractmethod, ABC
import pygame as pg
from geometry.vector import Vector
from config import ButtonSettings as bs
from config import DefaultActorSettings as das
from config import ScreenSettings as ss
from config import PhysicsSettings as ps


class IRendered(ABC):
    @abstractmethod
    def draw(
        self, screen_surface: pg.Surface, convert_position, zoomLevel: float
    ) -> None:
        """convert_position - функция для преобразования позиции объекта в его позицию на экране"""
        pass


class IPhysics(ABC):
    @abstractmethod
    def update(self, entities: list["IPhysics"]) -> None:
        pass


class Entity(pg.sprite.Sprite, IRendered):
    def __init__(self, position: Vector, size: Vector, name="") -> None:
        super().__init__()
        self.size = size
        self.name = name
        self.rect = pg.Rect(*position.pair(), *size.pair())
        self.set_position(position)

    def set_position(self, new_position: Vector):
        self.__position = new_position
        self.rect.centerx = int(self.__position.x)
        self.rect.centery = int(self.__position.y)

    def shift_position(self, delta_position: Vector):
        self.set_position(self.__position + ss.FPS_clock.get_time() * delta_position)

    def get_position(self):
        return self.__position

    @abstractmethod
    def draw(self, screen_surface: pg.Surface, convert_position, zoomLevel: float):
        pass

    @staticmethod
    def collide_entities(entity, entities: list["Entity"]) -> list["Entity"]:
        """entities: сущности с которыми может пересекаться объект
        return: сущности с которыми пересекается объект (исключая себя)"""
        collide_group = pg.sprite.spritecollide(entity, entities, False)
        if entity in collide_group:
            collide_group.remove(entity)
        return collide_group


class RenderedRect(Entity):
    def __init__(self, position: Vector, size: Vector, color: tuple[int], name="Rect"):
        super().__init__(position, size, name)
        self.color = color

    def draw(self, screen_surface: pg.Surface, convert_position, zoomLevel: float):
        size = self.size * zoomLevel
        position_on_screen: Vector = convert_position(self.get_position())
        pg.draw.rect(
            screen_surface,
            self.color,
            pg.Rect(*position_on_screen.pair(), *size.pair()),
        )


class Bar(Entity):
    """Шкала здоровья/маны и прочего"""

    def __init__(
        self,
        position: Vector,
        size: Vector,
        color: tuple[int],
        bg_color: tuple[int],
        name="Bar",
    ):
        super().__init__(position, size, name)
        self.percent = 1
        self.ident = 0.1 * Vector(self.size.y, self.size.y)
        self.bg_bar = RenderedRect(position, size, bg_color)
        self.movable_bar = RenderedRect(
            position + self.ident, size - 2 * self.ident, color
        )

    def draw(self, screen_surface: pg.Surface, convert_position, zoomLevel: float):
        self.bg_bar.set_position(self.get_position())
        self.movable_bar.set_position(self.get_position() + self.ident)
        self.movable_bar.size.x = self.percent * (self.bg_bar.size.x - 2 * self.ident.x)

        self.bg_bar.draw(screen_surface, convert_position, zoomLevel)
        self.movable_bar.draw(screen_surface, convert_position, zoomLevel)

    def update(self, percent: float):
        self.percent = max(0, min(percent, 1))


class PhysicsEntity(Entity, IPhysics):
    def __init__(
        self,
        image_path: str,
        is_movable: bool,
        name="PhysicsEntity",
        mass=1.0,
        velocity=Vector(0, 0),
        acceleration=Vector(0, 0),
    ) -> None:
        self.image = pg.image.load(image_path)
        position = Vector(0, 0)
        size = Vector(self.image.get_width(), self.image.get_height())
        super().__init__(position, size, name)
        self.mass = mass
        self.is_movable = is_movable
        self.velocity = velocity
        self.acceleration = acceleration

    def draw(self, screen_surface: pg.Surface, convert_position, zoomLevel: float):
        size = self.size * zoomLevel
        position_on_screen: Vector = convert_position(self.get_position())
        image = pg.transform.scale(self.image, size.pair())
        screen_surface.blit(image, position_on_screen.pair())


class StaticEntity(PhysicsEntity):
    def __init__(self, image_path: str, is_interactive: bool) -> None:
        self.is_interactive = is_interactive
        super().__init__(image_path, False)


class MovableEntity(PhysicsEntity):
    def __init__(self, image_path: str, name="MovableEntity") -> None:
        super().__init__(image_path, True, name)
        self.move_direction = Vector(0, 0)  # задаёт только направление
        self.speed = das.speed
        self.mass = das.mass

    def move(self, entities: list[PhysicsEntity]) -> None:
        delta_position = self.move_direction.get_normalization() * self.speed
        self.shift_position(delta_position)
        # проверка на столкновение
        collide_group = MovableEntity.collide_entities(self, entities)
        if not collide_group:
            return
        print("collision")
        self.shift_position(-delta_position)

    def update(self, entities: list[PhysicsEntity]) -> None:
        self.move(entities)

    # for entity in entities:
    #     if self == entity:
    #         continue
    #     if pg.sprite.collide_rect(self, entity):


class Player(MovableEntity):
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
        self.trackedEntity: Entity = None

    def set_tracked_entity(self, entity: Entity, speed=0.0):
        assert 0 <= speed <= 1
        self.speed = speed
        self.trackedEntity = entity

    def render(self, screen_surface: pg.Surface, entities: list[Entity]) -> None:
        position_on_camera = lambda position: position
        if self.trackedEntity is not None:
            s = self.speed
            entity = self.trackedEntity
            position = Vector(self.rect.x, self.rect.y)
            size = Vector(self.rect.width, self.rect.height)

            target_position = entity.get_position() + entity.size / 2
            self.world_position = self.world_position * (1 - s) + target_position * s
            offset = position + size / 2 - (self.zoomLevel * self.world_position)
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
        self.display_entities = pg.sprite.Group()

    def render(self, screen_surface: pg.Surface) -> None:
        self.camera.render(screen_surface, self.display_entities)

    def set_tracked_entity(self, entity: Entity, speed=0.0):
        self.camera.set_tracked_entity(entity, speed)

    def add_entity(self, entity: Entity):
        self.display_entities.add(entity)

    def add_entities(self, entities: list[Entity]):
        for entity in entities:
            self.add_entity(entity)

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

    def add_entity_on_layer(self, l_name: str, entity: Entity):
        self.layers[l_name].add_entity(entity)

    def add_entities_on_layer(self, l_name: str, entities: list[Entity]):
        self.layers[l_name].add_entities(entities)

    def set_tracked_entity(self, l_name: str, entity: Entity, speed=0.0):
        self.layers[l_name].set_tracked_entity(entity, speed)

    def render(self) -> None:
        for l_name in self.sorted_layers:
            self.layers[l_name].render(self.surface)

    def get_entities(self, l_name: str) -> list[Entity]:
        return self.layers[l_name].display_entities

    @abstractmethod
    def event_tracking(self, event: pg.event.Event):
        pass

    @abstractmethod
    def update(self):
        pass
