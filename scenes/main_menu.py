
import pygame

from config import BG_COLOR_DEFAULT

from scenes.scene import Scene

class MainMenu(Scene):
    def __init__(self, game):
        super().__init__(game)

    def draw(self, screen: pygame.Surface):
        screen.fill(BG_COLOR_DEFAULT)