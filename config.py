# конфигурации - поля классов
from enum import Enum
import pygame as pg
from os.path import exists
from typing import Any
from dataclasses import dataclass

from character_type import PhysicsStats, ChParts

start_body = { ChParts.CORE : 2,
        ChParts.SHELL: 1,
        ChParts.LEGS: 0,
        ChParts.BODY: 1}

def get_header_dyn_menu():
    header_market = {'Back': 'Pause'}
    for name, i in start_body.items(): 
        header_market[f"{name.value}"] = 'Market'
    return header_market


@dataclass
class Vertex:
    """Вершины, использумые в графах"""
    Name: Any 

class Colors:
    black = (0, 0, 0)
    silver = (40, 40, 40)
    red = (125, 0, 0)
    green = (0, 125, 0)
    turquoise = (0, 154, 200)
    pink = (255, 56, 103)
    white = (255,255,255)


class ScreenSettings:
    width, height = 500, 500
    game_title = "Evolution"
    bg_color = Colors.turquoise

    camera_speed = 1  # the speed of the camera keeping up with the player
    camera_zoom = 1


class GameSettings:
    FPS_clock = pg.time.Clock()
    FPS = 40
    developer_mode = False
    log_file_name = "log.txt"
    default_color = Colors.red
    default_button_color = Colors.silver
    bar_scale = 1.25
    bar_aspect_ratio = 8

    @staticmethod
    def dt():
        return GameSettings.FPS_clock.get_time()


class PhysicsSettings:
    max_speed = 0.2
    separation_speed = max_speed * 0.1
    friction_coefficient = 0.01
    error = 0.001
    repulsion_force = 100
    energy_absorption = 0.1

    default_entity_physics_stats = PhysicsStats(
        speed=0,
        mass=1,
        friction_coeff=0,
        scale_speed=0,
    )


class Action(Enum):
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"
    INVULNERABILITY = "invulnerability"


class ButtonSettings:
    move_buttons = {
        Action.RIGHT: pg.K_d,
        Action.LEFT: pg.K_a,
        Action.UP: pg.K_w,
        Action.DOWN: pg.K_s,
    }


class StartCharacter:
    body = {
        ChParts.CORE: 2,
        ChParts.SHELL: 1,
        ChParts.LEGS: 0,
        ChParts.BODY: 1,
    }


class DefaultCharacterSettings:
    speed = PhysicsSettings.max_speed * 0.5
    mass = 10
    max_HP = 10
    damage = 1
    invulnerability = 500

    movement = list(ButtonSettings.move_buttons.keys())
    effects = [Action.INVULNERABILITY]





class MenuSetting():
    color_bg = Colors.black
    color_text = Colors.white
    font = '8-BIT WONDER.TTF' if exists('8-BIT WONDER.TTF') else pg.font.get_default_font()
    menu_stract = {'vertices': [Vertex('Main'),Vertex('Pause'), Vertex('Market'), Vertex('Quit'), Vertex('Game')],
                'transitions' : {Vertex('Main').Name: {'Start': Vertex('Game'), 
                                                        'Exit': Vertex('Quit')},
                                 
                                Vertex('Pause').Name: {'Items': Vertex('Market'),
                                                    'Continue': Vertex('Game'), 
                                                    'Main menu': Vertex('Main'), 
                                                    'Exit': Vertex('Quit')},
                                
                                Vertex('Market').Name: {'Back': Vertex('Pause'), 
                                                    'core': Vertex('Market'), 
                                                    'shell' : Vertex('Market'), 
                                                    'legs': Vertex('Market'), 
                                                    'body': Vertex('Market') },
                                
                                Vertex('Game').Name: {'Escape': Vertex('Pause')}
                                },
                'current_vertice': Vertex('Main'),
                'finish_vertices': [Vertex('Quit')]
                }

    
    
    main_header = {'Start': 'Game', 'Exit': 'Quit'}
    pause_header = {'Items': 'Market','Continue': 'Game', 'Main menu': 'Main', 'Exit': 'Quit'}
    market_header = get_header_dyn_menu()
    menu = [Vertex('Main').Name,Vertex('Pause').Name, Vertex('Market').Name, Vertex('Quit').Name, Vertex('Game').Name]
    cursor = '*'
    
    
class Settings(
    DefaultCharacterSettings,
    PhysicsSettings,
    ButtonSettings,
    GameSettings,
    ScreenSettings,
    StartCharacter,
):
    pass


def print_in_log_file(msg: str):
    if not GameSettings.developer_mode:
        return
    with open(GameSettings.log_file_name, "a") as f:
        # f.write(msg + "\n")
        print(msg)


# if __name__ == "__main__":
