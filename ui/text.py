
import pygame


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font,
    color: pygame.Color,
    position,
    centered=False,
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


def draw_prompt(
    surface: pygame.Surface,
    text: str,
    font: pygame.font,
    position=None,
    align="midbottom",
    color=(255, 255, 255),
    background_color=(20, 24, 32, 210),
    dialogue_manager=None,
):
    """Desenha um aviso de interação no mesmo visual usado por outros prompts do jogo."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()

    if position is None:
        position = (surface.get_width() // 2, surface.get_height() - 18)
    setattr(rect, align, position)

    background_rect = rect.inflate(20, 10)
    if dialogue_manager is not None:
        background_rect = dialogue_manager.stack_bubble_rect(background_rect)
        rect.center = background_rect.center

    background = pygame.Surface(background_rect.size, pygame.SRCALPHA)
    background.fill(background_color)
    surface.blit(background, background_rect.topleft)
    surface.blit(rendered, rect)