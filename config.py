# конфигурации - поля классов
from enum import Enum
import pygame as pg

from character_type import PhysicsStats, ChParts


class Colors:
    black = (0, 0, 0)
    silver = (40, 40, 40)
    red = (125, 0, 0)
    green = (0, 125, 0)
    turquoise = (0, 154, 200)
    pink = (255, 56, 103)


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
        ChParts.CORE : 2,
        ChParts.SHELL: 1,
        ChParts.LEGS: 0,
        ChParts.BODY: 1
    }

class DefaultCharacterSettings:
    speed = PhysicsSettings.max_speed * 0.5
    mass = 10
    max_HP = 10
    damage = 1
    invulnerability = 500

    movement = list(ButtonSettings.move_buttons.keys())
    effects = [Action.INVULNERABILITY]



class MainMenu():
    Start = "Start game"
    LEFT = "Exit"
    
class PauseMenu():
    Continue = "Continue game"
    Item = "Market"
    Restart = "Restart game"

class MarketMenu():
    Back = "Back"

class MenuSetting(
    MainMenu, 
    PauseMenu, 
    MarketMenu
):
    pass
    
        

class Settings(
    DefaultCharacterSettings,
    PhysicsSettings,
    ButtonSettings,
    GameSettings,
    ScreenSettings,
    StartCharacter
):
    pass


def print_in_log_file(msg: str):
    if not GameSettings.developer_mode:
        return
    with open(GameSettings.log_file_name, "a") as f:
        # f.write(msg + "\n")
        print(msg)
