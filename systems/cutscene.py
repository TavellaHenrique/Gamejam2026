import pygame


class Cutscene:
    # Move uma entidade por pontos usando segmentos horizontais e verticais.

    def __init__(self):
        # Mantém o estado do trajeto atual.
        self.entity = None
        self.path = []
        self.path_index = 0
        self.is_active = False

    def start(self, entity, points):
        # Aceita um ou mais destinos e valida a API de movimento necessária.
        points = [pygame.Vector2(point) for point in points]
        if not points:
            raise ValueError("Uma cutscene precisa de pelo menos um destino.")
        if not callable(getattr(entity, "move_towards", None)):
            raise TypeError("A entidade precisa implementar move_towards().")

        self.entity = entity
        self.path = self._build_path(entity.position, points)
        self.path_index = 0
        self.is_active = bool(self.path)

    @staticmethod
    def _build_path(start, points):
        # Cotovelos ortogonais mantêm cada trecho horizontal ou vertical.
        path = []
        current = pygame.Vector2(start)

        for point in points:
            horizontal_corner = pygame.Vector2(point.x, current.y)
            for waypoint in (horizontal_corner, point):
                if waypoint != current:
                    path.append(waypoint)
                    current = waypoint

        return path

    def update(self, delta_time, bounds=None, obstacles=()):
        # Avança um ponto por quadro e encerra ao completar todos os destinos.
        if not self.is_active:
            return

        target = self.path[self.path_index]
        if self.entity.move_towards(
            target,
            delta_time,
            bounds=bounds,
            obstacles=obstacles,
            keep_walking=self.path_index < len(self.path) - 1,
        ):
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.is_active = False
