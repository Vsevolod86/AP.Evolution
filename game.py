from enum import Enum
import pygame as pg

from engine import Character, Bar, Player, Screen, Obstacle, Entity
from config import Settings
from config import Colors, print_in_log_file
from geometry.vector import Vector
from character_type import RedBacteria, GreenBacteria


class GameScreen(Screen):
    def __init__(self, surface: pg.Surface) -> None:
        w, h, i = surface.get_width(), surface.get_height(), 5
        display_area = pg.Rect(i, i, w - 2 * i, h - 2 * i)
        super().__init__(surface, display_area)
        self.LN = Enum("LN", ["BG", "MAP", "INTERFACE"])  # Layers Names

        # BackGround
        self.add_layer(self.LN.BG, 1)
        bg = Entity(Vector(w, h), Vector(i, i), self.LN.BG, Settings.bg_color)
        self.add_entities_on_layer(self.LN.BG, bg)

        # MAP
        self.add_layer(self.LN.MAP, 2)

        self.player = Player(GreenBacteria(), name="player")
        self.add_entities_on_layer(self.LN.MAP, self.player)
        self.set_tracked_entity(self.LN.MAP, self.player, Settings.camera_speed)

        enemy1 = Character(GreenBacteria(), name="enemy1")
        enemy1.set_position(Vector(90, 20))
        enemy2 = Character(RedBacteria(), name="enemy2")
        enemy2.set_position(Vector(80, 20))
        self.add_entities_on_layer(self.LN.MAP, [enemy1, enemy2])

        rect = Obstacle("images/tmp.png", name="rect")
        rect.set_position(Vector(100, 100))
        self.add_entities_on_layer(self.LN.MAP, rect)

        # INTERFACE
        self.add_layer(self.LN.INTERFACE, 3)

        barHP = Bar(
            Vector(50, 10), Vector(30, 30), color=Colors.green, bg_color=Colors.silver
        )
        barHP.update_load(0.8)
        self.add_entities_on_layer(self.LN.INTERFACE, barHP)

        self.set_camera_zoom(Settings.camera_zoom)

    def process_event(self, event: pg.event.Event):
        """Отслеживание событий"""
        self.player.process_event(event)

    def process_entities(self):
        for entity in self.get_entities(self.LN.MAP):
            entity.process(self.get_entities(self.LN.MAP))
            if not entity.is_exist:
                self.layers[self.LN.MAP].remove(entity)

    def set_camera_zoom(self, zoom: float):
        for layer_name in [self.LN.MAP, self.LN.BG]:
            self.layers[layer_name].set_zoom(zoom)


class Game:
    def __init__(self) -> None:
        pg.init()
        # Окно игры: размер, позиция
        self.surface = pg.display.set_mode((Settings.width, Settings.height))
        pg.display.set_caption(Settings.game_title)

        self.is_game_run = True
        self.game_screen = GameScreen(self.surface)

    def event_tracking(self, screen: Screen):
        """Отслеживание событий"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_game_run = False  # "закрыть игру"
            elif self.is_game_run:
                screen.process_event(event)

    def run(self) -> None:
        """Запуск цикла игры, который
        1) считывает события
        2) обновляет объекты
        3) рендерит объекты
        """

        current_screen: Screen = self.game_screen
        # Цикл игры
        cadr = 0
        while self.is_game_run:
            print_in_log_file(f"{cadr = :_^40}")
            cadr += 1
            Settings.FPS_clock.tick(Settings.FPS)
            self.event_tracking(current_screen)

            current_screen.process_entities()

            self.surface.fill(Colors.pink)
            current_screen.render()

            # Обновление экрана (всегда в конце цикла)
            pg.display.flip()

        pg.quit()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
