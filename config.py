# конфигурации - поля классов
import pygame


class ScreenSettings:
    width, height = 500, 500
    game_title = "Evolution"
    bg_color = (0, 154, 200)
    FPS = 30
    zoom = 2


class ButtonSettings:
    move_buttons = {
        "right": pygame.K_d,
        "left": pygame.K_a,
        "up": pygame.K_w,
        "down": pygame.K_s,
    }
