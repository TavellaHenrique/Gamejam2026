import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS
)

def main():
    # Inicia os módulos importados dentro do pygame que requerem inicialização obrigatória
    pygame.init()

    # Define as propriedades da janela
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Define o título da janela
    pygame.display.set_caption("Fatec Presas Abertas")

    # Classe de temporizador que ajuda a controlar o taxa de quadros
    clock = pygame.time.Clock()

    # Flag que define se o jogo deve continuar executando
    running = True

    # Loop principal
    while running:
        # Faz os quadros avançarem (até o máximo passado como argumento) e armazena o tempo passado entre cada um
        delta_time = clock.tick(FPS) // 1000 # milli

        running = manage_events()

        # Atualiza todos os elementos na tela
        pygame.display.flip()

    # Encerra a aplicação
    pygame.quit()

def manage_events():
    # Para cada evento detectado:
    for event in pygame.event.get():

        # Verifica o tipo do evento e faz a ação correspondente
        match event.type:
            case pygame.QUIT:
                return False

    # Se nenhum evento interromper a execução, ela continua (óbvio, mas necessário)
    return True

if __name__ == "__main__":
    main()