import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pygame

from game.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS
)

from game.game import Game

def main():
    # Recursos e dados usam caminhos relativos à pasta do pacote do jogo.
    os.chdir(Path(__file__).resolve().parent)

    # Inicia os módulos importados dentro do pygame que requerem inicialização obrigatória
    pygame.init()

    # Define as propriedades da janela
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Define o título da janela
    pygame.display.set_caption("Fatec Presas Abertas")

    # Classe de temporizador que ajuda a controlar o taxa de quadros
    clock = pygame.time.Clock()

    # Instância da classe que coordena o jogo
    game = Game()

    # Flag que define se o jogo deve continuar executando
    running = True

    # Loop principal
    while running:
        # Faz os quadros avançarem (até o máximo passado como argumento) e armazena o tempo passado entre cada um
        delta_time = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case _:
                    # O jogo trata atalhos globais antes de encaminhar o evento à cena.
                    if not game.handle_global_event(event):
                        game.scene_manager.handle_event(event)

        # Atualiza a lógica e desenha a cena usando o tempo desde o quadro anterior.
        if not game.inventory_open and not game.scene_manager.is_paused:
            game.scene_manager.update(delta_time)
        game.scene_manager.draw(screen)
        game.draw_inventory(screen)
        game.draw_debug_overlay(screen)

        # Atualiza todos os elementos na tela
        pygame.display.flip()

    # Encerra a aplicação
    pygame.quit()

if __name__ == "__main__":
    main()