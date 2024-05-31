from enum import Enum
import pygame as pg
import pygame_menu as pg_menu

from engine import Character, Bar, Player, Screen, Obstacle, Entity
from config import Settings
from config import Colors, print_in_log_file
from geometry.vector import Vector
from character_type import RedBacteria, GreenBacteria, ChParts
from menu import Menu


class GameScreen(Screen):
    def __init__(self, game, surface: pg.Surface) -> None:
        w, h, i = surface.get_width(), surface.get_height(), 5
        display_area = pg.Rect(i, i, w - 2 * i, h - 2 * i)
        super().__init__(surface, display_area)
        self.LN = Enum("LN", ["BG", "MAP", "INTERFACE"])  # Layers Names

        self.game = game
        
        
        # BackGround
        self.add_layer(self.LN.BG, 1)
        bg = Entity(Vector(w, h), Vector(i, i), self.LN.BG, Settings.bg_color)
        self.add_entities_on_layer(self.LN.BG, bg)

        # MAP
        self.add_layer(self.LN.MAP, 2)

        self.player = Player(GreenBacteria(), name="player")
        self.player.change_body_part(ChParts.SHELL, 1)
        self.player.change_body_part(ChParts.CORE, 1)
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
        # TODO: можно на камеру прямо навешивать, а не в отдельный слой выносить
        self.add_layer(self.LN.INTERFACE, 3)

        self.HPbar = Bar(
            Vector(100, 10), Vector(30, 30), color=Colors.green, bg_color=Colors.silver
        )
        self.HPbar.update_load(0.8)
        self.add_entities_on_layer(self.LN.INTERFACE, self.HPbar)

        self.set_camera_zoom(Settings.camera_zoom)


    def process_event(self, event: pg.event.Event):
        """Отслеживание событий"""
        self.player.process_event(event)

        
    def event_tracking(self):
        """Отслеживание событий"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.game_ranning  = False
                break
            else:
                self.process_event(event)

    

    def process_entities(self):
        for entity in self.get_entities(self.LN.MAP):
            entity.process(self.get_entities(self.LN.MAP))
            if not entity.is_exist:
                self.layers[self.LN.MAP].remove(entity)
        self.HPbar.update_load(self.player.HPbar.load)  # TODO: закастылил

    def set_camera_zoom(self, zoom: float):
        for layer_name in [self.LN.MAP, self.LN.BG]:
            self.layers[layer_name].set_zoom(zoom)
            
    def display_game(self):
        self.game_ranning = True
        while self.game_ranning:

            Settings.FPS_clock.tick(Settings.FPS)
            self.event_tracking()

            self.process_entities()

            self.surface.fill(Colors.pink)
            self.render()

            # Обновление экрана (всегда в конце цикла)

            pg.display.flip()


class Game:
    def __init__(self) -> None:
        pg.init()
        # Окно игры: размер, позиция
        self.surface = pg.display.set_mode((Settings.width, Settings.height))
        pg.display.set_caption(Settings.game_title)

        self.status = None
        self.main_menu = Menu(self, self.surface, ['Start','Exit'], "Main")
        self.pause_menu = Menu(self, self.surface, ['Items','Continue', 'Restart', 'Exit'], "Pause")
        self.market_menu = Menu(self, self.surface, ['Back','item 1', 'item 2', 'item 3', 'item 4'], "Market")
        # self.game_screen = GameScreen(self, self.surface)
    
        self.current_menu = self.main_menu
        
        self.is_game_run = True
        self.is_game_pause = False

    # def event_tracking(self, screen: Screen):
    #     """Отслеживание событий"""
    #     for event in pg.event.get():
    #         if event.type == pg.QUIT:
    #             self.is_game_run = False  # "закрыть игру"
    #         elif self.is_game_run:
    #             screen.process_event(event)

    def run(self) -> None:
     
        while self.is_game_run:
            self.current_menu.display_menu()
            if self.status == "Exit":
                break
            if self.status == "Start":
                self.game_screen = GameScreen(self, self.surface)
                self.game_screen.display_game()
                self.current_menu = self.pause_menu
            if self.status == "Continue":
                self.game_screen.display_game()
                self.current_menu = self.pause_menu
            if self.status == "Restart":
                self.current_menu = self.main_menu
            if self.status == "Items":
                self.current_menu = self.market_menu
            if self.status == "Back":
                self.current_menu = self.pause_menu
            
        pg.quit()

    def unpaused(self):
        self.is_game_pause = False

    def paused(self):
        self.is_game_pause = True

        while self.is_game_pause:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    exit()

            if self.pause_menu.is_enabled():
                self.pause_menu.draw(self.surface)
            self.pause_menu.update(events)
            pg.display.flip()
        return

    def main_menu_run(self) -> None:
        self.main_menu.mainloop(self.surface)
        return

    def launch(self) -> None:

        # Создание основного меню(main_menu)
        theme = pg_menu.themes.THEME_DARK.copy()
        theme.title_bar_style = pg_menu.widgets.MENUBAR_STYLE_ADAPTIVE
        theme.widget_selection_effect = pg_menu.widgets.NoneSelection()
        self.main_menu = pg_menu.Menu(
            # enabled=True,
            theme=theme,
            height=Settings.height * 0.8,
            width=Settings.width * 0.8,
            onclose=pg_menu.events.EXIT,
            title="Main menu",
        )

        self.main_menu.add_button("Start", self.run)

        self.pause_menu = pg_menu.Menu(
            # enabled=True,
            theme=theme,
            height=Settings.height * 0.8,
            width=Settings.width * 0.8,
            onclose=pg_menu.events.EXIT,
            title="Pause",
        )

        self.pause_menu.add_button("Continue", self.unpaused)
        self.pause_menu.add_button("Restart", self.run)
        self.pause_menu.add_button("Back", self.main_menu_run)
        #

        self.main_menu_run()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
