from enum import Enum
import pygame as pg
import pygame_menu as pg_menu

from engine import Character, Bar, Player, Screen, Obstacle, Entity
from config import Settings
from config import Colors, print_in_log_file
from geometry.vector import Vector
from character_type import RedBacteria, GreenBacteria, ChParts, CharacterTypeController
from menu import Menu

start_body = { ChParts.CORE : 2,
        ChParts.SHELL: 1,
        ChParts.LEGS: 0,
        ChParts.BODY: 1}


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
        CTC = CharacterTypeController(GreenBacteria())

        self.list_limit = {ch.name.lower(): len(CTC.get_all_parts()[ch])  for ch in ChParts}
        print(self.list_limit)
        for name, i in start_body.items():
            self.player.change_body_part(name, i)

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
                self.player.clear_action_duration()
                return
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

            pg.display.flip()


class Game:
    def __init__(self) -> None:
        pg.init()
        # Окно игры: размер, позиция
        self.surface = pg.display.set_mode((Settings.width, Settings.height))
        pg.display.set_caption(Settings.game_title)

        self.status = None
        self.main_menu = Menu(self, self.surface, ['Start','Exit'], "Main")
        self.pause_menu = Menu(self, self.surface, ['Items','Continue', 'Main menu', 'Exit'], "Pause")
        self.market_menu = Menu(self, self.surface, ['Back'] + [ f"{name.value} {i}" for name, i in start_body.items()], "Market")
        
        self.current_menu = self.main_menu
        
        self.is_game_run = True
        self.is_game_pause = False


    def run(self) -> None:
     
        while self.is_game_run:
            print(self.status)
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
            if self.status == 'Main menu':
                self.current_menu = self.main_menu
            if self.status == "Items":
                self.current_menu = self.market_menu
            if self.status == "Back":
                self.current_menu = self.pause_menu
            if self.status in [ f"{name.value} {i}" for name, i in start_body.items()]:
                part = self.status[0:-2]
                index = int(self.status[-1])
                # print(part, index)
                index = 0 if self.game_screen.list_limit[part] == index + 1 else index + 1
                header_index = {'core': 1, 'shell' : 2, 'legs': 3, 'body': 4 }
                self.market_menu.rename_header(header_index[part], f"{part} {index}")
                change_part = None
                for ctc in ChParts:
                    if ctc.value == part:
                        change_part = ctc
                self.game_screen.player.change_body_part(change_part, index)
                start_body[change_part] = index
                # print(self.market_menu.list_header)
                
            
        pg.quit()


if __name__ == "__main__":
    new_game = Game()
    new_game.run()
