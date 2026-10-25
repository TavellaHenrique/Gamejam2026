import pygame


class Trigger:
    """Área genérica que detecta entrada de entidades."""

    def __init__(self, position=None, radius=None, rect=None, once=False):
        # A área precisa ser um retângulo ou um círculo completo.
        if rect is None and (position is None or radius is None):
            raise ValueError("Informe um retângulo ou posição e raio.")
        # Evita configuração ambígua com geometria retangular e circular juntas.
        if rect is not None and (position is not None or radius is not None):
            raise ValueError("Use retângulo ou círculo, não os dois.")
        # Um raio negativo não representa uma área válida.
        if radius is not None and radius < 0:
            raise ValueError("O raio do trigger não pode ser negativo.")

        self.position = (
            pygame.Vector2(position)
            if position is not None
            else None
        )
        self.radius = radius
        self.rect = pygame.Rect(rect) if rect is not None else None
        self.once = once
        self.has_triggered = False
        self._actors_inside = set()

    def contains(self, actor):
        """Indica se o centro lógico de uma entidade está dentro da área."""
        return self.contains_position(actor.position)

    def contains_position(self, position):
        """Indica se uma posição está dentro da área do gatilho."""
        if self.rect is not None:
            return self.rect.collidepoint(position)

        return self.position.distance_to(position) <= self.radius

    def update(self, actor):
        """Retorna True apenas quando a entidade entra pela primeira vez."""
        # Um gatilho de uso único não pode disparar novamente após sua ativação.
        if self.once and self.has_triggered:
            return False

        inside = self.contains(actor)
        was_inside = actor in self._actors_inside
        if inside:
            self._actors_inside.add(actor)
        else:
            self._actors_inside.discard(actor)

        # Só dispara na transição de fora para dentro, não a cada atualização.
        entered = inside and not was_inside
        if entered:
            self.has_triggered = True
        return entered

    def reset(self):
        """Permite que o trigger volte a ser ativado."""
        self.has_triggered = False
        self._actors_inside.clear()

    def draw(self, screen, color=(240, 210, 90)):
        """Desenha a área para ajudar a visualizar e depurar o trigger."""
        if self.rect is not None:
            pygame.draw.rect(screen, color, self.rect, width=2)
        else:
            pygame.draw.circle(
                screen,
                color,
                (round(self.position.x), round(self.position.y)),
                round(self.radius),
                width=2,
            )
