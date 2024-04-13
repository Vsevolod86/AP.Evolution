import pygame
from config import ScreenSettings


class Screen:
    def __init__(self) -> None:
        # Окно игры: размер, позиция
        self.surface = pygame.display.set_mode(ScreenSettings.size)
        pygame.display.set_caption(ScreenSettings.game_title)
        self.surface.fill(ScreenSettings.bg_color)

    def update(self) -> None:
        self.surface.fill(ScreenSettings.bg_color)
