from enum import Enum
import pygame as pg

from engine import Character, Bar, Player, Screen, Obstacle, Entity
from config import Settings
from config import Colors, print_in_log_file
from geometry.vector import Vector


class GameScreen(Screen):
    def __init__(self, surface: pg.Surface) -> None:
        super().__init__(surface)
        self.LN = Enum("LN", ["BG", "MAP", "INTERFACE"])  # Layers Names

        # BackGround
        w, h, i = surface.get_width(), surface.get_height(), 5
        self.add_layer(self.LN.BG, pg.Rect(i, i, w - 2 * i, h - 2 * i))
        bg = Entity(Vector(w, h), Vector(i, i), self.LN.BG, Settings.bg_color)
        self.add_entities_on_layer(self.LN.BG, bg)

        # MAP
        self.add_layer(self.LN.MAP, pg.Rect(i, i, w - 2 * i, h - 2 * i))

        self.player = Player("images/bacteria_green.png", "player")
        self.add_entities_on_layer(self.LN.MAP, self.player)
        self.set_tracked_entity(self.LN.MAP, self.player, Settings.camera_speed)

        enemy1 = Character("images/bacteria_orange.png", name="enemy1")
        enemy1.set_position(Vector(90, 20))
        enemy2 = Character("images/bacteria_red.png", name="enemy2")
        enemy2.set_position(Vector(80, 20))
        enemy2.mass = 0.1
        self.add_entities_on_layer(self.LN.MAP, [enemy1, enemy2])

        rect = Obstacle("images/tmp.png", name="rect")
        rect.set_position(Vector(100, 100))
        self.add_entities_on_layer(self.LN.MAP, rect)

        # INTERFACE
        self.add_layer(self.LN.INTERFACE, pg.Rect(i, i, w - 2 * i, h - 2 * i))

        barHP = Bar(
            Vector(50, 10), Vector(30, 30), color=Colors.green, bg_color=Colors.silver
        )
        barHP.update_load(0.8)
        self.add_entities_on_layer(self.LN.INTERFACE, barHP)

        self.set_camera_zoom(Settings.camera_zoom)

    def event_tracking(self, event: pg.event.Event):
        """Отслеживание событий"""
        self.player.process_event(event)

    def process_entities(self):
        # self.player.process_entities(self.get_entities(self.LN.MAP))
        for entity in self.get_entities(self.LN.MAP):
            entity.process(self.get_entities(self.LN.MAP))
            print_in_log_file(f"{entity.name}, {entity.v}")

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
                screen.event_tracking(event)

    def run(self) -> None:
        """Запуск цикла игры, который
        1) считывает события
        2) обновляет объекты
        3) рендерит объекты
        """

        main_screen: Screen = self.game_screen
        # Цикл игры
        cadr = 0
        while self.is_game_run:
            print_in_log_file(f"{cadr = :_^40}")
            cadr += 1
            Settings.FPS_clock.tick(Settings.FPS)
            # print_in_log_file("Event")
            self.event_tracking(main_screen)

            # print_in_log_file("Update")
            main_screen.process_entities()

            # print_in_log_file("Render")
            self.surface.fill(Colors.pink)
            main_screen.render()

            # Обновление экрана (всегда в конце цикла)
            pg.display.flip()

        pg.quit()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
