"""Controla deslocamentos roteirizados de entidades durante uma cutscene."""

import pygame


class Cutscene:
    """Move uma entidade por pontos usando apenas segmentos horizontais e verticais."""

    def __init__(self):
        """Cria uma cutscene inativa, sem entidade ou pontos de destino."""
        self.entity = None
        self.path = []
        self.path_index = 0
        self.is_active = False

    def start(self, entity, points):
        """Inicia um trajeto por pelo menos dois pontos (x, y)."""
        points = [pygame.Vector2(point) for point in points]
        if len(points) < 2:
            raise ValueError("Uma cutscene precisa de pelo menos dois pontos.")
        if not callable(getattr(entity, "move_towards", None)):
            raise TypeError("A entidade precisa implementar move_towards().")

        self.entity = entity
        self.path = self._build_path(entity.position, points)
        self.path_index = 0
        self.is_active = bool(self.path)

    @staticmethod
    def _build_path(start, points):
        """Cria cotovelos ortogonais de comprimento mínimo entre os pontos."""
        path = []
        current = pygame.Vector2(start)

        for point in points:
            # Mover primeiro no eixo X e depois no Y produz distância Manhattan mínima.
            horizontal_corner = pygame.Vector2(point.x, current.y)
            for waypoint in (horizontal_corner, point):
                if waypoint != current:
                    path.append(waypoint)
                    current = waypoint

        return path

    def update(self, delta_time, bounds=None, obstacles=()):
        """Avança a entidade até o próximo ponto e encerra ao concluir o trajeto."""
        if not self.is_active:
            return

        target = self.path[self.path_index]
        if self.entity.move_towards(
            target,
            delta_time,
            bounds=bounds,
            obstacles=obstacles,
        ):
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.is_active = False
