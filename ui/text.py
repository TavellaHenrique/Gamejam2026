
import pygame


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font,
    color: pygame.Color,
    position,
    centered = False
):
    """Renderiza texto e posiciona-o pelo canto superior esquerdo ou pelo centro."""
    text_surface = font.render(text, True, color)

    # O retângulo calculado pelo Pygame permite alinhar o texto pela posição pedida.
    rect = text_surface.get_rect()

    if centered:
        rect.center = position
    else:
        rect.topleft = position

    # Desenha a imagem renderizada na superfície de destino.
    surface.blit(text_surface, rect)