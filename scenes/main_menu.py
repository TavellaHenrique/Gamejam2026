
import pygame

from config import BG_COLOR_DEFAULT

from ui.text import draw_text
from scenes.scene import Scene

class MainMenu(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.title_font = pygame.font.Font("assets/fonts/stairsnslabs.ttf", 32)
        self.body_font = pygame.font.Font("assets/fonts/stairsnslabs.ttf", 16)

    def handle_event(self, event: pygame.Event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            # TODO: Iniciar jogo
            pass

    def draw(self, screen: pygame.Surface):
        screen.fill(BG_COLOR_DEFAULT)

        center_x = screen.get_width() // 2

        draw_text(
            screen,
            "Fatec Presas Abertas",
            self.title_font,
            (255, 255, 255),
            (center_x, 220),
            centered=True
        )

        draw_text(
            screen,
            "Pressione ENTER para iniciar",
            self.body_font,
            (200, 200, 200),
            (center_x, 320),
            centered = True
        )


