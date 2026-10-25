import math

import pygame


class CameraManager:
    """Gerencia o mundo virtual, viewport, rastreamento, zoom e renderização."""

    def __init__(
        self,
        world_width,
        world_height,
        screen_width,
        screen_height,
        zoom=1.0,
        max_zoom=4.0,
        background_color=(0, 0, 0),
    ):
        dimensions = (world_width, world_height, screen_width, screen_height)
        if any(dimension <= 0 for dimension in dimensions):
            raise ValueError("As dimensões do mundo e da tela devem ser positivas.")
        if max_zoom <= 0:
            raise ValueError("O zoom máximo deve ser positivo.")

        self.world_width = round(world_width)
        self.world_height = round(world_height)
        self.screen_width = round(screen_width)
        self.screen_height = round(screen_height)
        rounded_dimensions = (
            self.world_width,
            self.world_height,
            self.screen_width,
            self.screen_height,
        )
        if any(dimension <= 0 for dimension in rounded_dimensions):
            raise ValueError("As dimensões arredondadas devem ser positivas.")
        self.max_zoom = max_zoom
        self.min_zoom = min(
            self.screen_width / self.world_width,
            self.screen_height / self.world_height,
        )
        if self.max_zoom < self.min_zoom:
            raise ValueError(
                "O zoom máximo não pode ser menor que o zoom mínimo."
            )
        self.world_surface = pygame.Surface(
            (self.world_width, self.world_height),
            pygame.SRCALPHA,
        )
        self.position = pygame.Vector2(
            self.world_width / 2,
            self.world_height / 2,
        )
        self.follow_target = None
        self.zoom = self._clamp_zoom(zoom)
        self.target_zoom = self.zoom
        self.background_color = background_color
        self.follow_smoothing = 1.0
        self._move_start = None
        self._move_target = None
        self._zoom_start = self.zoom
        self._zoom_target = self.zoom
        self._animation_elapsed = 0.0
        self._animation_duration = 0.0
        self._last_render_rect = pygame.Rect(
            0,
            0,
            self.screen_width,
            self.screen_height,
        )

    @property
    def is_animating(self):
        """Indica se uma transição de posição ou zoom ainda está em curso."""
        return self._move_target is not None

    @property
    def viewport_size(self):
        """Tamanho da região visível em coordenadas do mundo."""
        return pygame.Vector2(
            min(self.world_width, self.screen_width / self.zoom),
            min(self.world_height, self.screen_height / self.zoom),
        )

    @property
    def viewport_rect(self):
        """Retângulo inteiro da região visível no mundo virtual."""
        size = self.viewport_size
        left = round(self.position.x - size.x / 2)
        top = round(self.position.y - size.y / 2)
        width = min(self.world_width, max(1, round(size.x)))
        height = min(self.world_height, max(1, round(size.y)))
        left = max(0, min(left, self.world_width - width))
        top = max(0, min(top, self.world_height - height))
        return pygame.Rect(left, top, width, height)

    @property
    def render_rect(self):
        """Retorna o retângulo ocupado pela câmera na tela."""
        return self._last_render_rect.copy()

    def follow(self, target):
        """Define o alvo que a câmera mantém centralizado."""
        self.follow_target = target

    def stop_following(self):
        """Para de rastrear o alvo atual sem alterar a posição da câmera."""
        self.follow_target = None

    def set_zoom(self, zoom, duration=0.25):
        """Anima para um nível de zoom, mantendo a proporção da tela."""
        if duration < 0:
            raise ValueError("A duração do zoom não pode ser negativa.")

        self.target_zoom = self._clamp_zoom(zoom)
        self._zoom_start = self.zoom
        self._zoom_target = self.target_zoom
        self._move_start = self.position.copy()
        self._move_target = self._clamp_position(
            self.position,
            zoom=self._zoom_target,
        )
        self._animation_elapsed = 0.0
        self._animation_duration = duration
        if duration == 0:
            self.zoom = self.target_zoom
            self.position = self._clamp_position(self.position)
            self._zoom_start = self.zoom
            self._zoom_target = self.zoom
            self._finish_animation()

    def move_to(self, position, duration=0.5, zoom=None):
        """Anima a câmera até uma posição e, opcionalmente, aplica zoom."""
        if duration < 0:
            raise ValueError("A duração do movimento de câmera não pode ser negativa.")

        target = pygame.Vector2(position)
        self._move_start = self.position.copy()
        self._zoom_start = self.zoom
        self._zoom_target = (
            self.zoom if zoom is None else self._clamp_zoom(zoom)
        )
        self._move_target = self._clamp_position(
            target,
            zoom=self._zoom_target,
        )
        self.target_zoom = self._zoom_target
        self._animation_elapsed = 0.0
        self._animation_duration = duration
        self.stop_following()
        if duration == 0:
            self.position = self._move_target.copy()
            self.zoom = self._zoom_target
            self._finish_animation()

    def update(self, delta_time):
        """Avança animações e mantém o alvo centralizado quando não há pan."""
        if delta_time < 0:
            raise ValueError("O tempo de atualização não pode ser negativo.")

        if self.is_animating:
            if self._move_start is None or self._move_target is None:
                raise RuntimeError("A animação da câmera está sem um destino.")
            self._animation_elapsed += delta_time
            progress = min(
                1.0,
                self._animation_elapsed / self._animation_duration,
            )
            eased_progress = progress * progress * (3 - 2 * progress)
            self.zoom = (
                self._zoom_start
                + (self._zoom_target - self._zoom_start) * eased_progress
            )
            self.position = self._clamp_position(
                self._move_start.lerp(
                    self._move_target,
                    eased_progress,
                )
            )
            if progress >= 1.0:
                self.zoom = self._zoom_target
                self.position = self._clamp_position(self._move_target)
                self._finish_animation()
            return

        target = self._target_position(self.follow_target)
        if target is None:
            return

        target = self._clamp_position(target)
        smoothing = max(0.0, min(1.0, self.follow_smoothing))
        if smoothing == 1.0:
            self.position = target
        elif smoothing > 0:
            amount = 1 - math.exp(-smoothing * delta_time)
            self.position = self.position.lerp(target, amount)
        self.position = self._clamp_position(self.position)

    def render(self, screen):
        """Desenha apenas a região visível, escalando o recorte para a tela."""
        if screen.get_size() != (self.screen_width, self.screen_height):
            raise ValueError(
                "A superfície de destino precisa corresponder às dimensões "
                "configuradas para a câmera."
            )

        screen.fill(self.background_color)
        source_rect = self.viewport_rect
        visible_world = self.world_surface.subsurface(source_rect)
        destination_width = min(
            self.screen_width,
            max(1, round(source_rect.width * self.zoom)),
        )
        destination_height = min(
            self.screen_height,
            max(1, round(source_rect.height * self.zoom)),
        )
        if visible_world.get_size() == (
            destination_width,
            destination_height,
        ):
            rendered = visible_world
        else:
            rendered = pygame.transform.smoothscale(
                visible_world,
                (destination_width, destination_height),
            )

        destination = rendered.get_rect(center=screen.get_rect().center)
        screen.blit(rendered, destination)
        self._last_render_rect = destination
        return destination

    def world_to_screen(self, position):
        """Converte um ponto absoluto do mundo para a viewport renderizada."""
        position = pygame.Vector2(position)
        source = self.viewport_rect
        scale_x = self._last_render_rect.width / source.width
        scale_y = self._last_render_rect.height / source.height
        return pygame.Vector2(
            self._last_render_rect.left
            + (position.x - source.left) * scale_x,
            self._last_render_rect.top
            + (position.y - source.top) * scale_y,
        )

    def screen_to_world(self, position):
        """Converte um ponto da viewport renderizada para o mundo."""
        position = pygame.Vector2(position)
        source = self.viewport_rect
        scale_x = source.width / self._last_render_rect.width
        scale_y = source.height / self._last_render_rect.height
        return pygame.Vector2(
            source.left
            + (position.x - self._last_render_rect.left) * scale_x,
            source.top
            + (position.y - self._last_render_rect.top) * scale_y,
        )

    def _clamp_zoom(self, zoom):
        if zoom <= 0:
            raise ValueError("O zoom deve ser positivo.")
        return max(self.min_zoom, min(zoom, self.max_zoom))

    def _clamp_position(self, position, zoom=None):
        position = pygame.Vector2(position)
        if zoom is None:
            zoom = self.zoom
        viewport = pygame.Vector2(
            min(self.world_width, self.screen_width / zoom),
            min(self.world_height, self.screen_height / zoom),
        )
        half_width = viewport.x / 2
        half_height = viewport.y / 2
        return pygame.Vector2(
            max(half_width, min(position.x, self.world_width - half_width)),
            max(half_height, min(position.y, self.world_height - half_height)),
        )

    @staticmethod
    def _target_position(target):
        if target is None:
            return None
        return pygame.Vector2(getattr(target, "position", target))

    def _finish_animation(self):
        self._move_start = None
        self._move_target = None
        self._zoom_start = self.zoom
        self._zoom_target = self.zoom
        self.target_zoom = self.zoom
        self._animation_elapsed = 0.0
        self._animation_duration = 0.0
