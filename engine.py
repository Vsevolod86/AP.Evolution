from abc import abstractmethod, ABC
from typing import Callable, Iterable, Union, List, Type, Tuple
from os.path import exists
import pygame as pg
from geometry.vector import Vector
from config import Settings, Action
from config import Colors
from character_type import (
    CharacterTypeController,
    CharacterType,
    ChParts,
    CharacterStats,
)


# INTERFACES AND PRIMITIVES


class IRenderable(ABC):
    @abstractmethod
    def update(
        self,
        screen_surface: pg.Surface,
        convert_position: Callable[[Vector], Vector],
        zoom: float,
    ):
        pass


class IPhysicable(ABC):
    @abstractmethod
    def move(self, velocity) -> None:
        pass

    @abstractmethod
    def process(self, entities: List[Type["IPhysicable"]]) -> None:
        pass


class IPositionable(ABC):
    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def set_position(self, new_position: Vector) -> None:
        pass

    @abstractmethod
    def set_indent(self, new_indent: Vector) -> None:
        pass


class IEventProcessable(ABC):
    @abstractmethod
    def process_event(self, event: pg.event.Event):
        pass


class Model:
    def __init__(self, elements_type=object) -> None:
        self._elements_type = elements_type
        self._elements: list[self._elements_type] = []

    def add(self, element):
        if isinstance(element, Iterable):
            for e in element:
                assert isinstance(e, self._elements_type) and "недобавляемый элемент"
                self._elements.append(e)
        elif isinstance(element, self._elements_type):
            self._elements.append(element)
        else:
            assert False and "недобавляемый элемент"

    def get_elements(self):
        return self._elements

    def delete(self, index: int):
        del self._elements[index]

    def remove(self, element):
        self._elements.remove(element)

    def modify(self, index: int, new_element):
        self._elements[index] = new_element


# DISPLAYED ENTITIES


class Entity(pg.sprite.Sprite, IRenderable, IPositionable):
    def __init__(
        self,
        size: Vector,
        position=Vector(0, 0),
        name="Entity",
        color=Settings.default_color,
    ) -> None:
        super().__init__()
        self.size = size
        self.name = name
        self.color = color
        self._indent = Vector(0, 0)
        self.rect = pg.Rect(*position.pair(), *self.size.pair())
        self.set_position(position)
        self.sub_elements = SubElementModel()

    @property
    def center(self):
        return self.get_position() + self.size / 2

    @property
    def left(self):
        return self.get_position().x

    @property
    def right(self):
        return self.get_position().x + self.size.x

    @property
    def top(self):
        return self.get_position().y

    @property
    def bottom(self):
        return self.get_position().y + self.size.y

    @property
    def is_exist(self):
        return True

    def set_position(self, new_position: Vector) -> None:
        self.__position = self._indent + new_position
        self.rect.left = int(self.__position.x)
        self.rect.top = int(self.__position.y)

    def set_indent(self, new_indent: Vector) -> None:
        self._indent = new_indent

    def shift_position(self, delta_position: Vector) -> None:
        self.set_position(self.__position + delta_position)

    def get_position(self):
        return self.__position

    def update(
        self,
        screen_surface: pg.Surface,
        convert_position: Callable[[Vector], Vector],
        zoom: float,
    ):
        """convert_position - функция для преобразования позиции объекта в его позицию на экране"""
        size = self.size * zoom
        position_on_screen = convert_position(self.get_position())
        rect = pg.Rect(*position_on_screen.pair(), *size.pair())
        pg.draw.rect(screen_surface, self.color, rect)

    @staticmethod
    def collide_entities(
        entity, entities: List[Type["Entity"]]
    ) -> List[Type["Entity"]]:
        """entities: сущности с которыми может пересекаться объект
        return: сущности с которыми пересекается объект (исключая себя)"""
        collide_group = pg.sprite.spritecollide(entity, entities, False)
        if entity in collide_group:
            collide_group.remove(entity)
        return collide_group


class SubElement(IRenderable):
    def __init__(
        self,
        main_entity: Entity,
        sub_entity: Entity,
        z_index=1,
    ) -> None:
        """indent - отступ"""
        assert (
            main_entity != sub_entity
            and isinstance(sub_entity, Entity)
            and "элемент не может быть подэлементом самого себя"
        )
        self.main_entity = main_entity
        self.sub_entity = sub_entity
        self.z_index = z_index

    def update_position(self):
        self.sub_entity.set_position(self.main_entity.get_position())

    def update(
        self,
        screen_surface: pg.Surface,
        convert_position: Callable[[Vector], Vector],
        zoom: float,
    ):
        self.sub_entity.update(
            screen_surface=screen_surface,
            convert_position=convert_position,
            zoom=zoom,
        )

    def get_sub_entity(self):
        return self.sub_entity


class SubElementModel(Model, IRenderable):
    def __init__(self) -> None:
        super().__init__(elements_type=SubElement)
        self._elements: list[SubElement]

    def add(self, element: SubElement):
        super().add(element=element)
        self._elements = sorted(self._elements, key=lambda se: se.z_index)

    def update_position(self):
        for entity in self._elements:
            entity.update_position()

    def update(
        self,
        screen_surface: pg.Surface,
        convert_position: Callable[[Vector], Vector],
        zoom: float,
    ):
        for entity in self._elements:
            entity.update(
                screen_surface=screen_surface,
                convert_position=convert_position,
                zoom=zoom,
            )

    def remove_by_name(self, name: str):
        """Удаляет первый элемент с заданным именем"""
        for el in self._elements:
            if el.get_sub_entity().name == name:
                self.remove(el)
                break

    def get_sub_entity_by_name(self, name: str):
        for el in self._elements:
            if el.get_sub_entity().name == name:
                return el.get_sub_entity()
        assert False and "поиск несуществующего объекта"


class Bar(Entity):
    """Шкала здоровья, энергии и прочего"""

    def __init__(
        self,
        size: Vector,
        position=Vector(0, 0),
        name="Bar",
        color: Tuple[int] = Colors.green,
        bg_color: Tuple[int] = Colors.silver,
    ) -> None:
        super().__init__(size, position, name, bg_color)
        self.__percent = 1.0
        # Шкала
        self.indent = 0.1 * Vector(self.size.min(), self.size.min())
        self.movable_bar = Entity(
            size - 2 * self.indent, position + self.indent, "FG of " + name, color
        )
        self.movable_bar.set_indent(self.indent)
        self.sub_elements.add(SubElement(self, self.movable_bar, 2))

    @property
    def load(self):
        return self.__percent

    def update(
        self,
        screen_surface: pg.Surface,
        convert_position: Callable[[Vector], Vector],
        zoom: float,
    ):
        super().update(
            screen_surface=screen_surface,
            convert_position=convert_position,
            zoom=zoom,
        )
        self.sub_elements.update_position()
        self.sub_elements.update(screen_surface, convert_position, zoom)

    def update_load(self, percent: float):
        self.__percent = max(0, min(percent, 1))
        self.movable_bar.size.x = self.__percent * (self.size.x - 2 * self.indent.x)

    @staticmethod
    def create_bar(length: float):
        bar_size = Vector(length, length / Settings.bar_aspect_ratio)
        return Bar(size=bar_size)


class RasterEntity(Entity):
    def __init__(
        self,
        path2image: str,
        position=Vector(0, 0),
        name="Entity",
    ) -> None:
        self.__set_image(path2image)
        size = Vector(self.image.get_width(), self.image.get_height())
        super().__init__(
            size=size,
            position=position,
            name=name,
            color=Settings.default_color,
        )

    def __set_image(self, path2image: str):
        assert exists(path2image) and "несуществующий спрайт"
        self.image = pg.image.load(path2image)

    def update(
        self,
        screen_surface: pg.Surface,
        convert_position: Callable[[Vector], Vector],
        zoom: float,
    ):
        """convert_position - функция для преобразования позиции объекта в его позицию на экране"""
        size = self.size * zoom
        position_on_screen = convert_position(self.get_position())
        if Settings.developer_mode:
            super().update(
                screen_surface=screen_surface,
                convert_position=convert_position,
                zoom=zoom,
            )
        image = pg.transform.scale(self.image, size.pair())
        screen_surface.blit(image, position_on_screen.pair())


# PHYSICAL ENTITIES


class PhysicsEntity(RasterEntity, IPhysicable):
    def __init__(
        self,
        path2image: str,
        is_movable: bool,
        position=Vector(0, 0),
        name="PhysicsEntity",
        stats=Settings.default_entity_physics_stats,
        mass=1.0,
    ) -> None:
        self.stats = stats
        self.is_movable = is_movable
        self.velocity = Vector(0, 0)
        super().__init__(path2image=path2image, position=position, name=name)

    def get_collision_objs_pipeline(self) -> List[Callable[..., None]]:
        return [
            CollisionSystem.handle_collision,
        ]

    @property
    def is_static(self) -> bool:
        return not self.is_movable

    @property
    def m(self) -> float:
        return self.stats.mass

    @property
    def v(self) -> Vector:
        return self.velocity

    @property
    def speed(self):
        return self.stats.speed

    @property
    def friction_coeff(self):
        return self.stats.friction_coeff

    def move_position(self, delta_position: Vector) -> None:
        self.shift_position(delta_position * Settings.dt())

    def move(self, velocity) -> None:
        """Обновление скорости и позиции"""
        if self.is_static:
            return
        # ограничиваю скорость снизу
        if abs(velocity) <= Settings.error:
            velocity = Vector(0, 0)
            return
        # ограничиваю скорость сверху
        if Settings.max_speed < abs(velocity):
            velocity *= Settings.max_speed / abs(velocity)
        self.move_position(velocity)

    def process(self, entities: List[Type["PhysicsEntity"]]) -> None:
        if self.is_movable:
            self.apply_friction(Settings.friction_coefficient)
            self.move(self.v)
        # проверка коллизий
        for entity in Entity.collide_entities(self, entities):
            for callback in self.get_collision_objs_pipeline():
                callback(self, entity)

    def apply_friction(self, friction_coefficient: float) -> None:
        """Применение силы трения к объекту"""
        if abs(self.v) > 0:
            friction_coefficient = min(max(friction_coefficient, 0), 1)
            self.velocity *= 1 - friction_coefficient


class Obstacle(PhysicsEntity):
    def __init__(
        self,
        path2image: str,
        position=Vector(0, 0),
        name="Obstacle",
    ) -> None:
        super().__init__(
            path2image=path2image, is_movable=False, position=position, name=name
        )


class Character(PhysicsEntity):
    def __init__(
        self,
        character_type: CharacterType,
        position=Vector(0, 0),
        name="Character",
    ) -> None:
        self.CTC = CharacterTypeController(character_type)
        super().__init__(
            path2image=self.CTC.get_parts()[ChParts.BODY].path_to_sprite,
            is_movable=True,
            position=position,
            name=name,
        )
        self.__set_body_parts()
        self.__set_base_specifications()
        self.__set_HP_bar()
        self.__set_action_duration()

    def __set_body_parts(self):
        self.__parts: dict[ChParts, SubElement] = {}
        for part_type, part in self.CTC.get_parts().items():
            part_entity = RasterEntity(part.path_to_sprite, name=part_type.value)
            part_entity.set_indent(part.indent)
            self.__parts[part_type] = SubElement(
                self, part_entity, z_index=part.z_index
            )
            self.sub_elements.add(self.__parts[part_type])
            if part_type == ChParts.CORE:
                part_entity.set_indent(part.indent + self.center - part_entity.center)

    def __set_base_specifications(self):
        self.stats = CharacterStats()
        for part in self.CTC.get_parts().values():
            self.stats += part.stats

    def __set_HP_bar(self):
        self.HPbar = Bar.create_bar(self.size.x * Settings.bar_scale)
        indent = self.size - Vector(
            (self.center + self.HPbar.center).x, -self.HPbar.size.y * 0.2
        )
        self.HPbar.set_indent(indent)
        self.sub_elements.add(SubElement(self, self.HPbar, 1))

    def __set_action_duration(self):
        self.action_duration: dict[Action, int] = {}
        # key - название действия, value - время выполнения
        for action in Action:
            self.action_duration[action] = 0

    @property
    def damage(self):
        return self.stats.damage

    @property
    def max_HP(self):
        return self.stats.max_HP

    @property
    def HP(self):
        return self.stats.HP

    @property
    def is_exist(self):
        return self.HP > 0

    def get_collision_objs_pipeline(self) -> List[Callable[..., None]]:
        return super().get_collision_objs_pipeline() + [
            CollisionSystem.handle_attack,
        ]

    def process(self, entities: List[Type[PhysicsEntity]]):
        self.process_effects()
        self.process_motion_intent()
        super().process(entities)
        self.sub_elements.update_position()

    def process_motion_intent(self):
        if self.action_duration[Action.RIGHT]:
            self.velocity.x = self.speed
        if self.action_duration[Action.LEFT]:
            self.velocity.x = -self.speed
        if self.action_duration[Action.UP]:
            self.velocity.y = -self.speed
        if self.action_duration[Action.DOWN]:
            self.velocity.y = self.speed

        if abs(self.v) > self.speed:
            self.velocity *= self.speed / abs(self.v)

    def process_effects(self):
        for effect in Settings.effects:
            new_t = max(self.action_duration[effect] - Settings.dt(), 0)
            self.action_duration[effect] = new_t

    def get_damage(self, damager: Type["Character"]):
        if self.action_duration[Action.INVULNERABILITY] > 0:
            return
        self.stats.HP -= damager.damage
        self.action_duration[Action.INVULNERABILITY] = Settings.invulnerability

    def apply_friction(self, friction_coefficient: float) -> None:
        super().apply_friction(friction_coefficient + self.friction_coeff)

    def update(
        self,
        screen_surface: pg.Surface,
        convert_position: Callable[[Vector], Vector],
        zoom: float,
    ):
        self.HPbar.update_load(self.HP / self.max_HP)
        super().update(
            screen_surface=screen_surface,
            convert_position=convert_position,
            zoom=zoom,
        )
        self.sub_elements.update(
            screen_surface=screen_surface,
            convert_position=convert_position,
            zoom=zoom,
        )


class Player(Character, IEventProcessable):
    def __init__(self, character_type: CharacterType, name="Player") -> None:
        super().__init__(
            character_type=character_type,
            name=name,
        )
        self.__set_clamped_buttons()

    def __set_clamped_buttons(self):
        """Создаёт поля связанные с кнопоками"""
        self.buttons: dict[int, Action] = {}
        # key - номер кнопки в pygame, value - название действия
        list_buttons = [Settings.move_buttons]
        for buttons in list_buttons:
            for name, button in buttons.items():
                self.buttons[button] = name

    def process(self, entities: List[Type[PhysicsEntity]]):
        self.process_clamped_buttons()
        super().process(entities)

    def process_clamped_buttons(self):
        for name, _ in self.action_duration.items():
            if name in Settings.movement:
                if self.action_duration[name] != 0:
                    self.action_duration[name] += Settings.dt()

    def process_event(self, event: pg.event.Event):
        is_pressed = event.type == pg.KEYDOWN
        is_released = event.type == pg.KEYUP
        if is_pressed or is_released:
            if event.key in self.buttons:
                name = self.buttons[event.key]
                if is_pressed:
                    self.action_duration[name] += Settings.dt()
                if is_released:
                    self.action_duration[name] = 0


# ENTITY CONTROLLERS


class CollisionSystem:

    @staticmethod
    def handle_collision(obj1: PhysicsEntity, obj2: PhysicsEntity):
        """Обработка столкновения"""
        if obj1.is_static and obj2.is_static:
            return
        elif obj1.is_movable and obj2.is_movable:
            CollisionSystem._handle_movables_collision(obj1, obj2)
        else:
            m_obj = obj1 if obj1.is_movable else obj2
            s_obj = obj1 if obj1.is_static else obj2
            CollisionSystem._handle_movable_and_static_collision(m_obj, s_obj)

        if obj1.rect.colliderect(obj2.rect):
            CollisionSystem.handle_repulsion(obj1, obj2)

    @staticmethod
    def _handle_movables_collision(obj1: PhysicsEntity, obj2: PhysicsEntity):
        new_velocity = lambda v1, m1, v2, m2: ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
        v1 = obj1.v
        v2 = obj2.v
        obj1.velocity = new_velocity(v1, obj1.m, v2, obj2.m)
        obj2.velocity = new_velocity(v2, obj2.m, v1, obj1.m)

    @staticmethod
    def _handle_movable_and_static_collision(
        movable_obj: PhysicsEntity, static_obj: PhysicsEntity
    ):
        # Вычисляем вектор "вхождения" подвижного объекта в неподвижный
        delta = Vector(0, 0)

        if movable_obj.v.x > 0:
            delta.x = static_obj.left - movable_obj.right
        elif movable_obj.v.x < 0:
            delta.x = static_obj.right - movable_obj.left

        if movable_obj.v.y > 0:
            delta.y = static_obj.top - movable_obj.bottom
        elif movable_obj.v.y < 0:
            delta.y = static_obj.bottom - movable_obj.top

        # Корректируем позицию и скорость объекта
        if abs(delta.x) < abs(delta.y):
            delta.y = 0
            movable_obj.velocity.x *= -(1 - Settings.energy_absorption)
        else:
            delta.x = 0
            movable_obj.velocity.y *= -(1 - Settings.energy_absorption)
        movable_obj.shift_position(delta)

    @staticmethod
    def handle_repulsion(obj1: PhysicsEntity, obj2: PhysicsEntity):
        """Применение силы отталкивания к объектам"""
        MIN_DISTANCE = 0.01
        distance = max(abs(obj1.center - obj2.center), MIN_DISTANCE)
        intersection_coeff = max(Settings.repulsion_force / distance, 0.1)

        direction_of_move = (obj1.center - obj2.center).get_normalization()
        if abs(direction_of_move) == 0:
            direction_of_move = Vector(1, 0)

        d_pos = intersection_coeff * Settings.separation_speed * direction_of_move
        obj1.move(d_pos)
        obj2.move(-d_pos)

    @staticmethod
    def handle_attack(obj1: Character, obj2: Character):
        if isinstance(obj1, Character) and isinstance(obj2, Character):
            obj1.get_damage(obj2)
            obj2.get_damage(obj1)


class Camera(Entity):
    """
    Класс обладающий областью видимости, который при помощи методов отображет объекты в ней.\\
    При помощи метода set_tracked_entity, можно прикрепить камеру к сущности и следить за ней.
    """

    def __init__(
        self,
        size: Vector,
        position=Vector(0, 0),
        name="Camera",
        zoom=1.0,
    ) -> None:
        super().__init__(
            size=size,
            position=position,
            name=name,
            color=Settings.default_color,
        )
        self.zoom = zoom
        self.world_position = Vector(0.0, 0.0)
        self.ratio_speed = 0.0
        self.tracked_entity: Entity = None

    def set_tracked_entity(self, entity: Entity, ratio_speed=0.0):
        assert (
            0 <= ratio_speed <= 1 and "ratio_speed вышло за пределы возможной скорости"
        )
        self.ratio_speed = ratio_speed
        self.tracked_entity = entity

    def set_zoom(self, new_zoom: float):
        self.zoom = new_zoom

    def render(self, screen_surface: pg.Surface, entities: List[Type[Entity]]) -> None:
        position_on_camera = lambda position: position
        if self.tracked_entity is not None:
            s = self.ratio_speed
            entity = self.tracked_entity

            target_position = entity.get_position() + entity.size / 2
            self.world_position = self.world_position * (1 - s) + target_position * s
            offset = (
                self.get_position() + self.size / 2 - (self.zoom * self.world_position)
            )
            position_on_camera = lambda position: (self.zoom * position) + offset

        # START render
        screen_surface.set_clip(self.rect)

        # render entities
        for e in entities:
            e.update(screen_surface, position_on_camera, self.zoom)

        # FINISH render
        screen_surface.set_clip(None)

    @staticmethod
    def create_by_rect(rect: pg.Rect, name="Camera", zoom=1.0):
        position = Vector(rect.x, rect.y)
        size = Vector(rect.width, rect.height)
        return Camera(size=size, position=position, name=name, zoom=zoom)


class Layer(Model):
    """Контейнер для сущностей и камеры отображаемой их"""

    def __init__(self, camera: Camera, z_index: int = 1) -> None:
        super().__init__(elements_type=Entity)
        self._elements: list[Entity]
        self.z_index = z_index
        self.camera = camera

    def set_tracked_entity(self, entity: Entity, speed=0.0):
        self.camera.set_tracked_entity(entity, speed)

    def set_zoom(self, new_zoom: float):
        self.camera.set_zoom(new_zoom)

    def render(self, screen_surface: pg.Surface) -> None:
        self.camera.render(screen_surface, self._elements)


class Screen(IEventProcessable):
    """Набор слоёв"""

    def __init__(self, surface: pg.Surface, display_area: pg.Rect) -> None:
        self.surface = surface
        self.display_area = display_area
        self.layers: dict[str, Layer] = {}
        self.sorted_layers: list[str] = []

    def add_layer(self, l_name: str, z_index: int = 1):
        camera = Camera.create_by_rect(self.display_area)
        self.layers[l_name] = Layer(camera, z_index)
        tmp = sorted(self.layers.items(), key=lambda it: it[1].z_index)
        self.sorted_layers = list(zip(*tmp))[0]

    def add_entities_on_layer(self, l_name: str, entities: Union[Entity, Iterable]):
        self.layers[l_name].add(entities)

    def get_entities(self, l_name: str) -> List[Type[Entity]]:
        return self.layers[l_name].get_elements()

    def set_tracked_entity(self, l_name: str, entity: Entity, speed=0.0):
        self.layers[l_name].set_tracked_entity(entity, speed)

    def render(self) -> None:
        for l_name in self.sorted_layers:
            self.layers[l_name].render(self.surface)

    @abstractmethod
    def process_event(self, event: pg.event.Event):
        pass

    @abstractmethod
    def process_entities(self):
        pass
