from dataclasses import dataclass
from os.path import exists
from collections import defaultdict
from enum import Enum
from config import Settings


# Части тела


@dataclass(frozen=True)
class BodyPart:
    """Содержит путь к спрайту части тела"""

    path_to_sprite: str

    def __post_init__(self):
        assert exists(self.path_to_sprite) and "не существует выбранного спрайта"


@dataclass(frozen=True)
class Body(BodyPart):
    """Содержит дополнительные статы персонажа"""

    max_HP: int


@dataclass(frozen=True)
class Legs(BodyPart):
    """Содержит дополнительные статы персонажа"""

    speed: int


@dataclass(frozen=True)
class Shell(BodyPart):
    """Содержит дополнительные статы персонажа"""

    max_HP: int
    damage: int


@dataclass(frozen=True)
class Core(BodyPart):
    """Преумножает статы персонажа"""

    scale_HP: float
    scale_speed: float


class ChParts(Enum):
    """CharacterParts"""

    CORE = "core"
    SHELL = "shell"
    LEGS = "legs"
    BODY = "body"


# Типы тел


class CharacterType:
    def __init__(self) -> None:
        self.parts: dict[ChParts, list[BodyPart]] = defaultdict(list)
        self._set_cores()
        self._set_bodies()
        self._set_legs()
        self._set_shells()

    @property
    def _path(self):
        return Settings.path_to_character_parts

    def _set_cores(self):
        self.parts[ChParts.CORE].append(Core(self._path + "core1.png", 1, 1))

    def _set_bodies(self):
        pass

    def _set_legs(self):
        pass

    def _set_shells(self):
        pass

    def get_pasrts(self) -> dict[ChParts, list[BodyPart]]:
        return self.parts


class GreenBacteria(CharacterType):
    def _set_bodies(self):
        self.parts[ChParts.BODY].append(Body(self._path + "GB_body1.png", 100))

    def _set_legs(self):
        self.parts[ChParts.LEGS].append(Legs(self._path + "GB_legs1.png", 0.1))

    def _set_shells(self):
        self.parts[ChParts.SHELL].append(Shell(self._path + "GB_shell1.png", 50, 0))


class RedBacteria(CharacterType):
    def _set_bodies(self):
        self.parts[ChParts.BODY].append(Body(self._path + "RB_body1.png", 50))

    def _set_legs(self):
        self.parts[ChParts.LEGS].append(Legs(self._path + "RB_legs1.png", 0.2))

    def _set_shells(self):
        self.parts[ChParts.SHELL].append(Shell(self._path + "RB_shell1.png", 10, 1))


# Управление телом


class CharacterTypeController:
    CHARACTER_TYPES = [
        GreenBacteria,
        RedBacteria,
    ]

    def __init__(self, character_type: CharacterType) -> None:
        self.set_new_character_type(character_type)

    def set_new_character_type(self, new_character_type: CharacterType):
        assert new_character_type in self.CHARACTER_TYPES and "выбран несуществующий тип персонажа"
        self.character_type = new_character_type()
        self.__selected_parts = {
            ChParts.BODY: 0,
            ChParts.SHELL: 0,
            ChParts.LEGS: 0,
            ChParts.CORE: 0,
        }

    def set_parts(
        self,
        new_parts: dict[ChParts, int],
    ):
        """В new_parts содержатся изменяеме части тела (key) и индексы новых частей (value)"""
        for part_type, part_ind in new_parts.items():
            self.__check_part(part_type, part_ind)
            self.__selected_parts[part_type] = part_ind

    def get_all_parts(self) -> dict[ChParts, list[BodyPart]]:
        return self.character_type.get_pasrts()

    def get_parts(self) -> dict[ChParts, BodyPart]:
        parts: dict[ChParts, BodyPart] = {}
        for part_type, part_ind in self.__selected_parts.items():
            parts[part_type] = self.get_all_parts()[part_type][part_ind]
        return parts

    def __check_part(self, part_type, part_ind):
        assert part_type in self.__selected_parts and "неопознанная часть"
        assert (
            0 <= part_ind < len(self.__selected_parts[part_type])
            and "выбрана несуществующая модификация"
        )


if __name__ == "__main__":
    green_b = RedBacteria()
    print(green_b.parts[ChParts.CORE])
    print(green_b.parts[ChParts.SHELL])
    print(green_b.parts[ChParts.LEGS])
    print(green_b.parts[ChParts.BODY])

    print()

    player = CharacterTypeController(RedBacteria)
    print(player.get_parts())
