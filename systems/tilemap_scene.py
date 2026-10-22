"""Shared camera and rendering setup for scenes backed by a tileset image."""

import math

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from scenes.scene import Scene
from systems.camera_manager import CameraManager


LABORATORY_OBSTACLES = (
    (0, 0, 862, 96),
    (905, 0, 55, 96),
    (0, 96, 14, 529),
    (946, 96, 14, 529),
    (14, 625, 932, 15),
    (62, 208, 73, 96),
    (174, 248, 73, 56), # cadeira/mesa primeira fileira, 3 colunas da esquerda
    (278, 248, 73, 56), # cadeira/mesa primeira fileira, 3 colunas da esquerda
    (462, 248, 73, 56), # cadeira/mesa primeira fileira, 3 colunas da esquerda
    (590, 208, 73, 96),
    (62, 332, 73, 88),
    (174, 332, 73, 88),
    (278, 332, 73, 88),
    (462, 332, 73, 88),
    (590, 332, 73, 88),
    (62, 432, 73, 98),
    (174, 432, 73, 98),
    (278, 432, 73, 98),
    (462, 432, 73, 98),
    (590, 432, 73, 98),
    (912, 115, 34, 510),
)


class TilemapScene(Scene):
    """Scene base that scales a background image and shows one map quadrant."""

    TILESET_SCALE = 1.5
    CAMERA_ZOOM_FACTOR = 0.5

    def __init__(self, game, tileset_path, player_spawn=None):
        super().__init__(game)
        self.player = game.player
        if player_spawn is None:
            player_spawn = game.player_spawn_point
        else:
            game.set_player_spawn_point(player_spawn)
        self.player.position.update(player_spawn)
        self.player.rect.center = player_spawn

        source_image = pygame.image.load(tileset_path).convert()
        map_size = (
            round(source_image.get_width() * self.TILESET_SCALE),
            round(source_image.get_height() * self.TILESET_SCALE),
        )
        self.map_image = pygame.transform.scale(source_image, map_size)
        self.bounds = self.map_image.get_rect()

        display = pygame.display.get_surface()
        screen_size = (
            display.get_size()
            if display is not None
            else (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        viewport_size = (map_size[0] / 4, map_size[1] / 4)
        zoom_x = screen_size[0] / viewport_size[0]
        zoom_y = screen_size[1] / viewport_size[1]
        if not math.isclose(zoom_x, zoom_y, rel_tol=0.001):
            raise ValueError(
                "A proporção da janela precisa corresponder à proporção "
                "do tileset para enquadrar exatamente um quadrante."
            )

        self.camera = CameraManager(
            *map_size,
            *screen_size,
            zoom=zoom_x * self.CAMERA_ZOOM_FACTOR,
        )
        self.camera.follow(self.player)
        self.camera.update(0)
        self.environment_obstacles = ()

    @classmethod
    def map_point(cls, position):
        """Converts a coordinate from the source tileset to world coordinates."""
        return pygame.Vector2(position) * cls.TILESET_SCALE

    @classmethod
    def map_rect(cls, rect):
        """Scales a rectangle measured against the source tileset."""
        return pygame.Rect(
            round(rect[0] * cls.TILESET_SCALE),
            round(rect[1] * cls.TILESET_SCALE),
            round(rect[2] * cls.TILESET_SCALE),
            round(rect[3] * cls.TILESET_SCALE),
        )

    def get_door_obstacles(self):
        """Returns every door's blocking rectangle in world coordinates."""
        return tuple(door.rect for door in getattr(self, "doors", ()))

    def update_camera(self, delta_time, cutscene_controller):
        """Follows the player except while a cutscene is moving the camera."""
        if cutscene_controller.waiting_for == "camera_movement":
            return
        self.camera.follow(self.player)
        self.camera.update(delta_time)

    def begin_world_draw(self):
        """Returns the camera surface with the enlarged tileset background."""
        self.camera.world_surface.blit(self.map_image, (0, 0))
        return self.camera.world_surface

    def render_world(self, screen):
        """Renders the camera's current map region onto the game window."""
        self.camera.render(screen)

    @staticmethod
    def draw_door_hint(screen, font, player, doors, prefix="E - "):
        """Shows an interaction hint for the nearest active transparent door."""
        for door in doors:
            if not door.can_interact(player):
                continue

            label = font.render(
                f"{prefix}{door.prompt}",
                True,
                (255, 255, 255),
            )
            label_rect = label.get_rect(
                midbottom=(screen.get_width() // 2, screen.get_height() - 18)
            )
            background_rect = label_rect.inflate(20, 10)
            background = pygame.Surface(background_rect.size, pygame.SRCALPHA)
            background.fill((20, 24, 32, 210))
            screen.blit(background, background_rect.topleft)
            screen.blit(label, label_rect)
            return
