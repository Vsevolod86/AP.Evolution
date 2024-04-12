from config import ScreenSettings
import pygame


class Screen:
    def __init__(self) -> None:
        # Окно игры: размер, позиция
        self.surface = pygame.display.set_mode(ScreenSettings.size)
        pygame.display.set_caption(ScreenSettings.game_title)
        self.surface.fill(ScreenSettings.bg_color)

    def update(self):
        self.surface.fill(ScreenSettings.bg_color)
