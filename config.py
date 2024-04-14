# конфигурации - поля классов
import pygame


class ScreenSettings:
    width, height = 500, 500
    game_title = "Evolution"
    bg_color = (0, 154, 200)
    black = (0, 0, 0)
    FPS = 30
    zoom = 2
    camera_speed  = 0.05 # the speed of the camera keeping up with the player
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
