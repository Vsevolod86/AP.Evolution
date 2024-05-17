import pygame as pg

from engine import MovableEntity, Bar, Player, RenderedRect, Screen
from config import ScreenSettings as ss
from config import Colors as crl
from geometry.vector import Vector
from enum import Enum


class GameScreen(Screen):
    def __init__(self, surface: pg.Surface) -> None:
        super().__init__(surface)
        self.LN = Enum("LN", ["BG", "MAP", "INTERFACE"])  # Layers Names

        # BackGround
        w, h, i = surface.get_width(), surface.get_height(), 5
        self.add_layer(self.LN.BG, pg.Rect(i, i, w - 2 * i, h - 2 * i))
        bg = RenderedRect(Vector(i, i), Vector(w, h), ss.bg_color)
        self.add_entity_on_layer(self.LN.BG, bg)

        # MAP
        self.add_layer(self.LN.MAP, pg.Rect(i, i, w - 2 * i, h - 2 * i))

        self.player = Player("images/bacteria_green.png", "player")
        self.add_entity_on_layer(self.LN.MAP, self.player)
        self.set_tracked_entity(self.LN.MAP, self.player, ss.camera_speed)

        enemy1 = MovableEntity("images/bacteria_orange.png", "enemy1")
        enemy1.mass = 2.0
        enemy1.set_position(Vector(90, 20))
        enemy2 = MovableEntity("images/bacteria_red.png", "enemy2")
        enemy2.set_position(Vector(80, 50))
        # enemy1.move_direction = Vector(-1, -1)
        self.add_entities_on_layer(self.LN.MAP, [enemy1, enemy2])

        # rect = RenderedRect(Vector(30, 70), Vector(30, 10), ss.bg_color)
        # rect.set_position(Vector(100, 100))
        # self.add_entity_on_layer(self.LN.MAP, rect)

        # INTERFACE
        self.add_layer(self.LN.INTERFACE, pg.Rect(i, i, w - 2 * i, h - 2 * i))

        barHP = Bar(Vector(30, 30), Vector(50, 10), crl.green, crl.silver)
        barHP.percent = 0.8
        self.add_entity_on_layer(self.LN.INTERFACE, barHP)

        self.set_camera_zoom(ss.camera_zoom)

    def event_tracking(self, event: pg.event.Event):
        """Отслеживание событий"""
        self.player.event_tracking(event)

    def update(self):
        # self.player.update(self.get_entities(self.LN.MAP))
        for entity in self.get_entities(self.LN.MAP):
            entity.update(self.get_entities(self.LN.MAP))

    def set_camera_zoom(self, zoomLevel: float):
        for layer_name in [self.LN.MAP, self.LN.BG]:
            self.layers[layer_name].set_zoom(zoomLevel)


class Game:
    def __init__(self) -> None:
        pg.init()
        # Окно игры: размер, позиция
        self.surface = pg.display.set_mode((ss.width, ss.height))
        pg.display.set_caption(ss.game_title)

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
            # print(f"{cadr = :_^40}")
            cadr+=1
            ss.FPS_clock.tick(ss.FPS)
            # print("Event")
            self.event_tracking(main_screen)

            # print("Update")
            main_screen.update()

            # print("Render")
            self.surface.fill(crl.pink)
            main_screen.render()

            # Обновление экрана (всегда в конце цикла)
            pg.display.flip()

        pg.quit()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
