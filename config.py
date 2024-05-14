# конфигурации - поля классов
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
    FPS = 3000
    zoom = 1
    camera_speed = 0.05  # the speed of the camera keeping up with the player
    camera_zoom = 2

    FPS_clock = pg.time.Clock()


class ButtonSettings:
    move_buttons = {
        "right": pg.K_d,
        "left": pg.K_a,
        "up": pg.K_w,
        "down": pg.K_s,
    }


class DefaultActorSettings:
    speed = 0.075
    weight = 10
