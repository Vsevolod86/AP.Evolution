# конфигурации - поля классов
import pygame


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
    FPS = 30
    zoom = 1
    camera_speed = 0.05  # the speed of the camera keeping up with the player
    camera_zoom = 2


class ButtonSettings:
    move_buttons = {
        "right": pygame.K_d,
        "left": pygame.K_a,
        "up": pygame.K_w,
        "down": pygame.K_s,
    }


class PlayerSettings:
    speed = 2.5
