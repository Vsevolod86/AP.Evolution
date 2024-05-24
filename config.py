# конфигурации - поля классов
from enum import Enum
import pygame as pg


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
    camera_zoom = 2


class GameSettings:
    FPS_clock = pg.time.Clock()
    FPS = 40
    developer_mode = True  # and False
    log_file_name = "log.txt"
    default_color = Colors.red
    bar_scale = 1.25
    bar_aspect_ratio = 5

    @staticmethod
    def dt():
        return GameSettings.FPS_clock.get_time()


class ButtonSettings:
    move_buttons = {
        "right": pg.K_d,
        "left": pg.K_a,
        "up": pg.K_w,
        "down": pg.K_s,
    }


class PhysicsSettings:
    max_speed = 0.2
    separation_speed = max_speed * 0.1
    friction_coefficient = 0.02
    error = 0.001


class DefaultActorSettings:
    speed = PhysicsSettings.max_speed * 0.5
    mass = 10
    weight = 10


class Settings(
    DefaultActorSettings,
    PhysicsSettings,
    ButtonSettings,
    GameSettings,
    ScreenSettings,
):
    pass


def print_in_log_file(msg: str):
    if not GameSettings.developer_mode:
        return
    with open(GameSettings.log_file_name, "a") as f:
        f.write(msg + "\n")
        print(msg)
