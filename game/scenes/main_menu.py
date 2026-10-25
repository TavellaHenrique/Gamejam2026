
import pygame

from game.config import BG_COLOR_DEFAULT

from game.ui.text import draw_text
from game.scenes.scene import Scene

from game.scenes.saguao import Saguao
from game.scenes.laboratorio1 import Laboratorio1


class MainMenu(Scene):
    """Menu inicial que aguarda o jogador iniciar a cena principal."""

    def __init__(self, game):
        """Configura as fontes do título e da instrução de início."""
        super().__init__(game)

        self.title_font = pygame.font.Font("assets/fonts/BPSHSfont.ttf", 124)
        self.body_font = pygame.font.Font("assets/fonts/typewcond_regular.otf", 54)
        self.body_font_credits = pygame.font.Font("assets/fonts/typewcond_regular.otf", 30)

    def handle_event(self, event: pygame.event): # type: ignore
        """Abre a cena de jogo quando o jogador pressiona Enter."""
        if event.type == pygame.KEYDOWN: # pyright: ignore[reportAttributeAccessIssue]
            if event.key == pygame.K_RETURN: # pyright: ignore[reportAttributeAccessIssue]
                self.game.scene_manager.change_scene(
                    Saguao(self.game)
                )
            elif event.key == pygame.K_1: # type: ignore
                self.game.scene_manager.change_scene(
                    Laboratorio1(self.game)
                )

    def draw(self, screen: pygame.Surface):
        """Desenha o fundo, o título e a instrução para iniciar o jogo."""
        screen.fill(BG_COLOR_DEFAULT)

        # Centraliza os dois textos horizontalmente na janela atual.
        center_x = screen.get_width() // 2
        width_10 = screen.get_width() // 10

        draw_text(
            screen,
            "\"Fatec Presas Abertas\"",
            self.title_font, # type: ignore
            (255, 255, 255), # type: ignore
            (center_x, 180),
            centered=True
        )

        draw_text(
            screen,
            "ENTER - Iniciar jogo",
            self.body_font, # type: ignore
            (200, 200, 200), # type: ignore
            (center_x, 380),
            centered = True
        )
        
        draw_text(
            screen,
            "Matheus Luna",
            self.body_font_credits, # type: ignore
            (200, 200, 200), # type: ignore
            (width_10 * 2.5, 500),
            centered = False
        )

        draw_text(
            screen,
            "Henrique Tavella",
            self.body_font_credits, # type: ignore
            (200, 200, 200), # type: ignore
            (width_10 * 5, 500),
            centered = False
        )
        
        draw_text(
            screen,
            "Rafaela Ferreira",
            self.body_font_credits, # type: ignore
            (200, 200, 200), # type: ignore
            (width_10 * 1, 550),
            centered = False
        )
        
        draw_text(
            screen,
            "Jane Mesquita",
            self.body_font_credits, # type: ignore
            (200, 200, 200), # type: ignore
            (width_10 * 4, 550),
            centered = False
        )
        
        draw_text(
            screen,
            "Ana Carolina",
            self.body_font_credits, # type: ignore
            (200, 200, 200), # type: ignore
            (width_10 * 7, 550),
            centered = False
        )