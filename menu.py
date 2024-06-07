from enum import Enum
import pygame as pg
from abc import abstractmethod, ABC
from dataclasses import dataclass

from engine import  Screen
from config import MenuSetting, Settings, Action
from typing import List, Dict, Type, Any

from character_type import ChParts


body = { ChParts.CORE : 2,
        ChParts.SHELL: 1,
        ChParts.LEGS: 0,
        ChParts.BODY: 1}



class Menu(Screen):
    def __init__(self, surface: pg.Surface, header: Dict) -> None:
    
        w, h, i = surface.get_width(), surface.get_height(), 5
        display_area = pg.Rect(i, i, w - 2 * i, h - 2 * i)
        super().__init__(surface, display_area)
        
        self.surface = surface

        self.status = None
        self.position_cursor = 0
        self.dict_header = header
        self.num_header = len(self.dict_header)
        self.position_list = list(self.dict_header.keys())
        
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
                if event.key == Settings.move_buttons[Action.UP]:
                    self.position_cursor_up()
                if event.key == Settings.move_buttons[Action.DOWN]:
                    self.position_cursor_down()
                if event.key == pg.K_SPACE:
                    self.run_display = False
                    self.status = self.position_list[self.position_cursor]
                            


    def process_entities(self):
        self.surface.fill(MenuSetting.color_bg)
        self.draw_cursor()
        height_step = int(self.surface.get_height()/(self.num_header+1))
        for i, header in enumerate(self.dict_header):
            self.draw_text(header, 20, 250, (1+i)*height_step)
        return


    def draw_cursor(self):
        self.draw_text(MenuSetting.cursor, 25, 100, (1 + self.position_cursor)*(int(self.surface.get_height()/(self.num_header+1))))

    def draw_text(self, text, size, x, y ):
        pg.font.init()
        font = pg.font.Font(MenuSetting.font, size)
        text_surface = font.render(text, True, MenuSetting.color_text)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.surface.blit(text_surface,text_rect)

    def blit_screen(self):
        self.surface.blit(self.surface, (0,0))
        pg.display.update()

    
    def display(self):
        self.run_display = True
        while self.run_display:
            Settings.FPS_clock.tick(Settings.FPS)
            
            self.process_event()
            
            self.process_entities()
   
            self.blit_screen()
  
    
class DynamicMenu(Menu):
    
    def __init__(self, game, surface: pg.Surface, header: Dict, body_parts) -> None:
        super().__init__( surface, header)
        self.body_parts = body_parts
        self.game = game
        
    def process_event(self):
        """Отслеживание событий"""
        choice_made = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit() 
            if event.type == pg.KEYDOWN:
                if event.key == Settings.move_buttons[Action.UP]:
                    self.position_cursor_up()
                if event.key == Settings.move_buttons[Action.DOWN]:
                    self.position_cursor_down()
                if event.key == pg.K_SPACE:
                    self.status = self.position_list[self.position_cursor]
                    choice_made = True
                    break
        
        if  choice_made:   
            if self.status == 'Back': 
                self.run_display = False
                return
            part = self.status
            change_part = None
            for ctc in self.body_parts:
                if ctc.value == part:
                    change_part = ctc

            index = self.game.player.body[change_part]
            index = 0 if self.game.list_limit[part] == index + 1 else index + 1
            self.game.player.change_body_part(change_part, index)
            self.game.player.body[change_part] = index
        else:
            if  self.status == None:
                return


        
        return
    
    def process_entities(self):
        
        self.surface.fill(MenuSetting.color_bg)
        self.draw_cursor()
        height_step = int(self.surface.get_height()/(self.num_header+1))

        self.draw_text('Back', 20, 250, height_step)
        
        header_index = {'core': 1, 'shell' : 2, 'legs': 3, 'body': 4 }
        for header in header_index :
            
            change_part = None
            for ctc in self.body_parts:
                if ctc.value == header:
                    change_part = ctc
            index = self.game.player.body[change_part]             
            self.draw_text(header+' '+str(index), 20, 250, (1+header_index[header])*height_step)

    
            


@dataclass
class Vertex:
    """Вершины, использумые в графах"""
    Name: Any 

@dataclass
class FSM():
    """Конечный автомат"""
    vertices: List[Type[Vertex]]
    transitions: Dict[Vertex, Dict[str, Vertex]]
    current_vertice: Type[Vertex]
    finish_vertices: List[Type[Vertex]]
    finish_work = False
    
    
    def make_step(self, trans: str ) -> Type[Vertex]:
        """Сделать шаг поменяв состояние"""
        if self.finish_work:
            return self.current_vertice
        
        dict_trans = self.transitions[self.current_vertice.Name]

        assert trans in list(dict_trans.keys()), f"Задан не коректный переход {trans} в вершине {self.current_vertice.Name}. Список доступных переходов из данной вершины {list(dict_trans.keys())}"
        
        self.current_vertice = self.transitions[self.current_vertice.Name][trans]
        self.__check_finish()
        return self.current_vertice
    
    def __check_finish(self) -> None:
        """Проверка нахождения в конечном состоянии"""
        self.finish_work = self.current_vertice in self.finish_vertices
        
        

if __name__ == "__main__":
    
    v = Vertex('www')
