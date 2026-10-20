
import pygame

from config import BG_COLOR_DEFAULT

from ui.text import draw_text
from scenes.scene import Scene

from scenes.game_scene import GameScene

class MainMenu(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.title_font = pygame.font.Font("assets/fonts/BPSHSfont.ttf", 124)
        self.body_font = pygame.font.Font("assets/fonts/typewcond_regular.otf", 54)

    def handle_event(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.scene_manager.change_scene(
                    GameScene(self.game)
                )

    def draw(self, screen: pygame.Surface):
        screen.fill(BG_COLOR_DEFAULT)

        center_x = screen.get_width() // 2

        draw_text(
            screen,
            "\"Fatec Presas Abertas\"",
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
            (center_x, 420),
            centered = True
        )
