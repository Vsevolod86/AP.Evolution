from dataclasses import dataclass, field
from os.path import exists
from collections import defaultdict
from enum import Enum
from copy import deepcopy
from geometry.vector import Vector
from typing import Dict, List, Type

# Части тела


class ChParts(Enum):
    """CharacterParts"""

    CORE = "core"
    SHELL = "shell"
    LEGS = "legs"
    BODY = "body"


@dataclass()
class PhysicsStats:
    speed: float = 0
    scale_speed: float = 1
    mass: float = 0
    scale_mass: float = 1
    friction_coeff: float = 0
    scale_friction_coeff: float = 1

    def __post_init__(self):
        for stat in self.absolute_stats:
            setattr(self, stat, self._get_scale_stat(stat))

    @property
    def all_stats(self):
        return list(vars(self).keys())

    @property
    def absolute_stats(self):
        return [stat for stat in vars(self).keys() if not stat.startswith("scale_")]

    @property
    def multiplying_stats(self):
        return [
            scale_stat
            for scale_stat in vars(self).keys()
            if scale_stat.startswith("scale_")
        ]

    def _get_scale_stat(self, stat: str):
        scale_stat = "scale_" + stat
        return getattr(self, stat) * getattr(self, scale_stat)

    def _get_unscale_stat(self, stat: str):
        scale_stat = "scale_" + stat
        return getattr(self, stat) / getattr(self, scale_stat)

    def _set_stat(self, stat: str, new_val: float):
        setattr(self, stat, new_val)

    def __iadd__(self, other: "PhysicsStats"):  # +=
        general_stats = set(self.absolute_stats) & set(other.absolute_stats)
        for stat in general_stats:
            scale_stat = "scale_" + stat
            # выделяю старые значения
            s1, s2 = getattr(self, scale_stat), getattr(other, scale_stat)
            c1 = self._get_unscale_stat(stat=stat)
            c2 = other._get_unscale_stat(stat=stat)
            # вычисляю новые значения
            new_scale = s1 + s2 - 1
            new_val = new_scale * (c1 + c2)
            # обновляю данные
            self._set_stat(scale_stat, new_scale)
            self._set_stat(stat, new_val)
        return self

    def __isub__(self, other: "PhysicsStats"):  # -=
        general_stats = set(self.absolute_stats) & set(other.absolute_stats)
        for stat in general_stats:
            scale_stat = "scale_" + stat
            # выделяю старые значения
            s1, s2 = getattr(self, scale_stat), getattr(other, scale_stat)
            c1 = self._get_unscale_stat(stat=stat)
            c2 = other._get_unscale_stat(stat=stat)
            # вычисляю новые значения
            new_scale = s1 - (s2 - 1)
            new_val = new_scale * (c1 - c2)
            # обновляю данные
            self._set_stat(scale_stat, new_scale)
            self._set_stat(stat, new_val)
        return self


@dataclass()
class CharacterStats(PhysicsStats):
    HP: float = 0
    scale_HP: float = 1
    max_HP: float = 0
    scale_max_HP: float = 1
    HP_regen_per_tick: float = 0
    scale_HP_regen_per_tick: float = 1
    damage: float = 0
    scale_damage: float = 1

    def __post_init__(self):
        super().__post_init__()
        self.HP = self.max_HP

    def __isub__(self, other: "PhysicsStats"):  # -=
        prev_HP = self.HP
        super().__isub__(other)
        self.HP = min(prev_HP, self.max_HP)
        return self


@dataclass()
class BodyPart:
    body_type: ChParts
    path_to_sprite: str
    indent: Vector
    stats: CharacterStats
    z_index: int = field(init=False)

    def __post_init__(self):
        assert exists(self.path_to_sprite) and "не существует выбранного спрайта"
        if self.body_type == ChParts.BODY:
            self.z_index = 1
        else:
            self.z_index = 2


# Типы тел


class CharacterType:
    def __init__(self) -> None:
        self.parts: dict[ChParts, list[BodyPart]] = defaultdict(list)
        self.add_core("core1.png", HP_regen_per_tick=0.001)
        self.add_core(
            "core2.png", HP_regen_per_tick=0.0015, scale_max_HP=1.2, scale_damage=1.2
        )
        self.add_core("core3.png", HP_regen_per_tick=0.001, scale_speed=1.35)

    @property
    def _path(self):
        path_to_character_parts_sprites = r"./images/"
        return path_to_character_parts_sprites

    def add_core(self, name: str, indent=Vector(0, 0), **stats):
        self._add_body_part(ChParts.CORE, name, indent, **stats)

    def add_body(self, name: str, indent=Vector(0, 0), **stats):
        self._add_body_part(ChParts.BODY, name, indent, **stats)

    def add_shell(self, name: str, indent=Vector(0, 0), **stats):
        self._add_body_part(ChParts.SHELL, name, indent, **stats)

    def add_legs(self, name: str, indent=Vector(0, 0), **stats):
        self._add_body_part(ChParts.LEGS, name, indent, **stats)

    def _add_body_part(
        self, body_type: ChParts, name: str, indent=Vector(0, 0), **stats
    ):
        self.parts[body_type].append(
            BodyPart(body_type, self._path + name, indent, CharacterStats(**stats))
        )

    def get_pasrts(self) -> Dict[Type[ChParts], List[Type[BodyPart]]]:
        return self.parts


class GreenBacteria(CharacterType):
    def __init__(self) -> None:
        super().__init__()
        self.add_body("GB_body1.png", max_HP=100, mass=12, friction_coeff=0.02)
        self.add_body("GB_body2.png", max_HP=200, mass=24, friction_coeff=0.03)
        self.add_legs("GB_legs1.png", speed=0.1, mass=1)
        self.add_shell("GB_shell1.png", max_HP=50, damage=5, mass=5)
        self.add_shell("GB_shell2.png", max_HP=100, damage=8, mass=10)
        self.add_shell("GB_shell3.png", max_HP=50, damage=4, mass=3, speed=0.05)


class RedBacteria(CharacterType):
    def __init__(self) -> None:
        super().__init__()
        self.add_body("RB_body1.png", max_HP=70, mass=8, friction_coeff=0)
        self.add_legs("RB_legs1.png", speed=0.12, mass=1)
        self.add_shell("RB_shell1.png", max_HP=20, damage=12, mass=4)
        self.add_shell("RB_shell2.png", max_HP=50, damage=10, mass=10)
        self.add_shell("RB_shell3.png", max_HP=40, damage=20, mass=10)


# Управление телом


class CharacterTypeController:
    CHARACTER_TYPES = [
        GreenBacteria,
        RedBacteria,
    ]

    def __init__(self, character_type: CharacterType) -> None:
        self.set_new_character_type(character_type)

    def set_new_character_type(self, new_character_type: CharacterType):
        assert (
            type(new_character_type) in self.CHARACTER_TYPES
            and "выбран несуществующий тип персонажа"
        )
        self.character_type = new_character_type
        self.__selected_parts: dict[ChParts, int] = {}
        for part_type in ChParts:
            self.__selected_parts[part_type] = 0

    def set_parts(
        self,
        new_parts: Dict[Type[ChParts], int],
    ):
        """В new_parts содержатся изменяеме части тела (key) и индексы новых частей (value)"""
        for part_type, part_ind in new_parts.items():
            self.__check_part(part_type, part_ind)
            self.__selected_parts[part_type] = part_ind

    def get_all_parts(self) -> Dict[Type[ChParts], List[Type[BodyPart]]]:
        return self.character_type.get_pasrts()

    def get_selected_parts(self) -> Dict[Type[ChParts], Type[BodyPart]]:
        parts: dict[ChParts, BodyPart] = {}
        for part_type, part_ind in self.__selected_parts.items():
            parts[part_type] = self.get_all_parts()[part_type][part_ind]
        return parts

    def __check_part(self, part_type, part_ind):
        assert part_type in self.__selected_parts and "неопознанная часть"
        assert (
            0 <= part_ind < len(self.get_all_parts()[part_type])
            and "выбрана несуществующая модификация"
        )


if __name__ == "__main__":
    # green_b = RedBacteria()
    # print(green_b.parts[ChParts.CORE])
    # print(green_b.parts[ChParts.SHELL])
    # print(green_b.parts[ChParts.LEGS])
    # print(green_b.parts[ChParts.BODY])

    # print()

    # player = CharacterTypeController(RedBacteria())
    # print(player.get_selected_parts())

    test_stats = CharacterStats(1, 3, 1, 3, 4, 1.5, 1, 1, 3, 1)
    print(test_stats)
    test_stats += test_stats
    print(test_stats)
