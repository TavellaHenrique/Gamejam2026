
import pygame

from config import BG_COLOR_DEFAULT

from ui.text import draw_text
from scenes.scene import Scene

from scenes.saguao import Saguao
from scenes.laboratorio1 import Laboratorio1


class MainMenu(Scene):
    """Menu inicial que aguarda o jogador iniciar a cena principal."""

    def __init__(self, game):
        """Configura as fontes do título e da instrução de início."""
        super().__init__(game)

        self.title_font = pygame.font.Font("assets/fonts/BPSHSfont.ttf", 124)
        self.body_font = pygame.font.Font("assets/fonts/typewcond_regular.otf", 54)

    def handle_event(self, event: pygame.event):
        """Abre a cena de jogo quando o jogador pressiona Enter."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.scene_manager.change_scene(
                    Saguao(self.game)
                )
            elif event.key == pygame.K_1:
                self.game.scene_manager.change_scene(
                    Laboratorio1(self.game)
                )

    def draw(self, screen: pygame.Surface):
        """Desenha o fundo, o título e a instrução para iniciar o jogo."""
        screen.fill(BG_COLOR_DEFAULT)

        # Centraliza os dois textos horizontalmente na janela atual.
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
            "ENTER - Iniciar jogo",
            self.body_font,
            (200, 200, 200),
            (center_x, 420),
            centered = True
        )
        draw_text(
            screen,
            "1 - Demonstração da câmera",
            self.body_font,
            (200, 200, 200),
            (center_x, 490),
            centered=True,
        )
