
import pygame

def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.Font,
    color: pygame.Color,
    position,
    centered = False
):
    text_surface = font.render(text, True, color)

    rect = text_surface.get_rect()

    if centered:
        rect.center = position
    else:
        rect.topleft = position

    surface.blit(text_surface, rect)