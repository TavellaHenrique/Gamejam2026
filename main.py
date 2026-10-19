# -- Importações --
# Biblioteca para desenvolvimento de jogos
import pygame

# Lógica do jogo
from game import Game

# Configurações do projeto
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

# -- Função principal --
def main():
    # Inicia os módulos importados pelo Pygame que demandam inicialização obrigatória
    pygame.init()

    # -- Configuração da janela gráfica (display) --
    # Inicia uma janela gráfica com as dimensões (x, y)
    # Essa variável recebe uma Surface (superfície) onde podemos desenhar elementos
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Define o título da janela
    pygame.display.set_caption("Fatec: Presas Abertas (Teste)")

    # -- Inicialização do jogo --
    # Instancia a classe com a lógica do jogo
    game = Game()

    # Flag usada para determinar se o jogo deve continuar executando
    running = True

    # Inicio do loop principal
    while running:
        # Define a taxa de atualização de imagens
        pygame.time.delay(60)

        # Gerencia os eventos do jogo
        running = manageEvents(game)

        # Define e configura os elementos que serão desenhados na tela
        game.draw(screen)

        # Atualiza graficamente os elementos
        pygame.display.flip()

    # Encerra a execução do jogo
    pygame.quit()

# -- Recebe cada evento e coordena as respostas --
# Retorna True para continuar a execução do jogo e False para encerrar o loop principal
def manageEvents(game: Game):
    # Captura todos os eventos
    for event in pygame.event.get():

        # Acionado para eventos de tecla pressionada
        if event.type == pygame.KEYDOWN:

            # Verifica o estado do jogo para corresponder com a(s) tecla(s) pressionada(s)
            match(game.state):
                case Game.START_MENU:
                    if event.key == pygame.K_RETURN:
                        game.state = Game.PLAYING
                    break
                case Game.PLAYING:
                    if event.key == pygame.K_RETURN:
                        game.state = Game.START_MENU
                    break
                case _:
                    pass

        # Acionado quando o usuário clica no botão de Encerrar aplicação (X no canto superior direito da janela)
        if event.type == pygame.QUIT:
            return False

    return True

if __name__ == "__main__":
    main()