from enum import Enum
import pygame as pg
from abc import abstractmethod, ABC
from dataclasses import dataclass

from engine import Character, Bar, Player, Screen, Obstacle, Entity
from geometry.vector import Vector
from config import MenuSetting, Settings, Action
from typing import List, Dict, Type, Any



class Menu(Screen):
    def __init__(self, game, surface: pg.Surface, header: Dict) -> None:
        # инит скрина
        w, h, i = surface.get_width(), surface.get_height(), 5
        display_area = pg.Rect(i, i, w - 2 * i, h - 2 * i)
        super().__init__(surface, display_area)
        
        self.surface = surface
        self.game = game
        
        self.display = True
        self.position_cursor = 0
        
        self.list_header = header
        self.num_header = len(self.list_header)
    
    def rename_header(self, i, name):
        self.list_header[i] = name
        
    def position_cursor_up(self):
        self.position_cursor = self.position_cursor - 1 if self.position_cursor != 0 else self.num_header - 1
        
    def position_cursor_down(self):
        self.position_cursor = self.position_cursor + 1 if self.position_cursor != self.num_header - 1 else 0
        
    
    @abstractmethod
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
                    self.g.status = self.list_header[self.position_cursor]
                            


    def process_entities(self):
        
        self.surface.fill(MenuSetting.color_bg)
        self.draw_cursor()
        height_step = int(self.surface.get_height()/(self.num_header+1))
        for i,header in enumerate(self.list_header):
            self.draw_text(header, 20, 250, (1+i)*height_step)

        return


    def draw_cursor(self):
        self.draw_text('*', 25, 100, (1 + self.position_cursor)*(int(self.surface.get_height()/(self.num_header+1))))

    def draw_text(self, text, size, x, y ):
        font = pg.font.Font(MenuSetting.font, size)
        text_surface = font.render(text, True, MenuSetting.color_text)
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

class StaticMenu(Menu):
    
    def __init__(self, game, surface: pg.Surface, header: Dict) -> None:
        super().__init__(game, surface, header)
    
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
                    self.g.status = self.list_header[self.position_cursor]
        
    
    
class DynamicMenu(Menu):
    
    def __init__(self, game, surface: pg.Surface, header: Dict, body_parts) -> None:
        super().__init__(game, surface, header)
        self.body_parts = body_parts
        
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
                    self.g.status = self.list_header[self.position_cursor]
                    break
                    
                    
        part = self.status[0:-2]
        index = int(self.status[-1])
        index = 0 if self.game.list_limit[part] == index + 1 else index + 1
        header_index = {'core': 1, 'shell' : 2, 'legs': 3, 'body': 4 }
        self.rename_header(header_index[part], f"{part} {index}")
        change_part = None
        for ctc in self.body_parts:
            if ctc.value == part:
                change_part = ctc
        self.game.player.change_body_part(change_part, index)
        self.game.start_body[change_part] = index
        
        self.status = part
        return
    
    
            


@dataclass
class Vertex:
    """Вершины, использумые в графах"""
    Name: Any 


dict = {'vertices': [Vertex('Main'),Vertex('Pause'), Vertex('Market'), Vertex('Quit'), Vertex('Game')],
        'transitions' : {Vertex('Main').Name: {'Start': Vertex('Game'), 
                                          'Exit': Vertex('Quit')},
                   Vertex('Pause').Name: {'Items': Vertex('Market'),
                                     'Continue': Vertex('Game'), 
                                     'Main menu': Vertex('Main'), 
                                     'Exit': Vertex('Quit')},
                   Vertex('Market').Name: {'Back': Vertex('Pause'), 
                                      'Core': Vertex('Market'), 
                                      'Shell' : Vertex('Market'), 
                                      'Legs': Vertex('Market'), 
                                      'Body': Vertex('Market') },
                   Vertex('Game').Name: {'Escape': Vertex('Pause')}
                   },
        'current_vertice': Vertex('Main'),
        'finish_vertices': [Vertex('Quit')]
        }

# vertices = ['Main',Vertex('Pause'), Vertex('Market'), Vertex('Quit')]
# transitions = {'Main': {'Start': Vertex('Pause'), 'Exit': Vertex('Quit')},
#                 Vertex('Pause'): {'Items': Vertex('Market'),'Continue': Vertex('Pause'), 'Main menu': 'Main', 'Exit': Vertex('Quit')},
#                 Vertex('Market'): {'Back': Vertex('Pause'), 'Core': Vertex('Market'), 'Shell' : Vertex('Market'), 'Legs': Vertex('Market'), 'Body': Vertex('Market') }
#                    }
# current_vertices = 'Main'
# finish_vertices = [Vertex('Quit')]


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
    # current_menu = FSM(**dict)
    # current_menu.make_step('Start')
    # current_menu.make_step('Escape')
    # print(current_menu.current_vertice)
    
    # v = Vertex('www')
    # # v.Name = "ff"
    # print(v.Name)