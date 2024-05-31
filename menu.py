from enum import Enum
import pygame as pg
from abc import abstractmethod, ABC

from engine import Character, Bar, Player, Screen, Obstacle, Entity
from geometry.vector import Vector
from config import MenuSetting, Settings


# K_SPACE, K_w, K_s 


current_cscreen = ["Main","Game","Pause","Market"]
font_name = '8-BIT WONDER.TTF'
BLACK, WHITE = (0, 0, 0), (255, 255, 255)


class Menu(Screen):
    def __init__(self, game, surface: pg.Surface, list_header, screen_name) -> None:
        # инит скрина
        w, h, i = surface.get_width(), surface.get_height(), 5
        display_area = pg.Rect(i, i, w - 2 * i, h - 2 * i)
        super().__init__(surface, display_area)
        
        self.surface = surface
        self.g = game
        
        self.display = True
        self.position_cursor = 0
        
        self.list_header = list_header
        self.screen = screen_name
        self.num_header = len(self.list_header)
  
        
    def position_cursor_up(self):
        self.position_cursor = self.position_cursor - 1 if self.position_cursor != 0 else self.num_header - 1
        
    def position_cursor_down(self):
        self.position_cursor = self.position_cursor + 1 if self.position_cursor != self.num_header - 1 else 0
        
        
    def process_event(self):
        """Отслеживание событий"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit() 
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.position_cursor_up()
                if event.key == pg.K_s:
                    self.position_cursor_down()
                if event.key == pg.K_SPACE:
                    self.run_display = False
                    self.g.status = self.list_header[self.position_cursor]
                            


    
    def process_entities(self):
        
        self.surface.fill(BLACK)
        self.draw_cursor()
        for i,header in enumerate(self.list_header):
            self.draw_text(header, 20, 250, (1+i)*(int(self.surface.get_height()/(self.num_header+1))))

        return


    def draw_cursor(self):
        self.draw_text('*', 25, 100, (1+self.position_cursor)*(int(self.surface.get_height()/(self.num_header+1))))

    def draw_text(self, text, size, x, y ):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.surface.blit(text_surface,text_rect)

    def blit_screen(self):
        self.surface.blit(self.surface, (0,0))
        pg.display.update()

    
    def display_menu(self):
        self.run_display = True
        while self.run_display:
            
            Settings.FPS_clock.tick(Settings.FPS)
            
            self.process_event()
            
            self.process_entities()
   
            self.blit_screen()

            
# if __name__ == "__main__":
    # pg.init()
    # surface = pg.display.set_mode((Settings.width, Settings.height))
    # pg.display.set_caption(Settings.game_title)
    
    # main_menu = Menu(surface, ['Start','Exit'], "Main")
    # pause_menu = Menu(surface, ['Items','Continue', 'Restart', 'Exit'], "Pause")
    # market_menu = Menu(surface, ['Back','item 1', 'item 2', 'item 3', 'item 4'], "Market")
    
    

    # pause_menu.display_menu()


    # pg.quit()