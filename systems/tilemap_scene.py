"""Shared camera and rendering setup for scenes backed by a tileset image."""

import math

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from entities.npc import NPC
from scenes.scene import Scene
from systems.camera_manager import CameraManager
from systems.collision import get_entity_hitbox


LABORATORY_OBSTACLES = (
    (0, 0, 862, 96),
    (905, 0, 55, 96),
    (0, 96, 14, 529),
    (946, 96, 14, 529),
    (14, 625, 932, 15),
)

LABORATORY_FURNITURE = (
    ((52, 205), (62, 208, 73, 96)),
    ((164, 205), (174, 248, 73, 56)),
    ((268, 205), (278, 248, 73, 56)),
    ((452, 205), (462, 248, 73, 56)),
    ((580, 205), (590, 208, 73, 96)),
    ((52, 317), (62, 332, 73, 88)),
    ((180, 317), (174, 332, 73, 88)),
    ((292, 317), (278, 332, 73, 88)),
    ((452, 317), (462, 332, 73, 88)),
    ((580, 317), (590, 332, 73, 88)),
    ((52, 429), (62, 432, 73, 98)),
    ((180, 429), (174, 432, 73, 98)),
    ((293, 437), (278, 432, 73, 98)),
    ((452, 429), (462, 432, 73, 98)),
    ((580, 429), (590, 432, 73, 98)),
)


class TilemapScene(Scene):
    """Scene base that scales a background image and shows one map quadrant."""

    TILESET_SCALE = 1.2 # Scale factor for the tileset image to world coordinates.
    CAMERA_ZOOM_FACTOR = 0.38 # Scale factor for the camera zoom to fit one quadrant of the tileset.
    _object_image_cache = {}
    _example_image_cache = {}

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
        self.source_map_image = source_image
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
        self.map_objects = []

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

    def create_map_object(
        self,
        image_path,
        position,
        collision_rect=None,
        occlusion_y=None,
    ):
        """Creates a placed, collidable foreground prop in map coordinates."""
        cache_key = (image_path, self.TILESET_SCALE)
        image = self._object_image_cache.get(cache_key)
        if image is None:
            source = pygame.image.load(image_path).convert_alpha()
            size = (
                round(source.get_width() * self.TILESET_SCALE),
                round(source.get_height() * self.TILESET_SCALE),
            )
            image = pygame.transform.scale(source, size)
            self._object_image_cache[cache_key] = image

        world_position = self.map_point(position)
        rect = image.get_rect(
            topleft=(round(world_position.x), round(world_position.y))
        )
        scaled_collision = None
        if collision_rect is not None:
            scaled_collision = pygame.Rect(
                round(world_position.x + collision_rect[0] * self.TILESET_SCALE),
                round(world_position.y + collision_rect[1] * self.TILESET_SCALE),
                round(collision_rect[2] * self.TILESET_SCALE),
                round(collision_rect[3] * self.TILESET_SCALE),
            )

        if occlusion_y is None:
            occlusion_y = image.get_height() / self.TILESET_SCALE / 2
        return TilemapObject(
            image,
            rect,
            scaled_collision,
            round(world_position.y + occlusion_y * self.TILESET_SCALE),
        )

    def create_map_object_from_example(
        self,
        example_path,
        crop_rect,
        position,
        collision_rect=None,
        occlusion_y=None,
    ):
        """Extracts an omitted prop from the example layer against the base map."""
        example = self._example_image_cache.get(example_path)
        if example is None:
            example = pygame.image.load(example_path).convert()
            self._example_image_cache[example_path] = example
        crop_rect = pygame.Rect(crop_rect)
        example_crop = example.subsurface(crop_rect).copy()
        base_crop = self.source_map_image.subsurface(crop_rect)
        for y in range(crop_rect.height):
            for x in range(crop_rect.width):
                source_pixel = example_crop.get_at((x, y))
                base_pixel = base_crop.get_at((x, y))
                difference = max(
                    abs(source_pixel.r - base_pixel.r),
                    abs(source_pixel.g - base_pixel.g),
                    abs(source_pixel.b - base_pixel.b),
                )
                if difference <= 20:
                    example_crop.set_at((x, y), (*source_pixel[:3], 0))

        image = pygame.transform.scale(
            example_crop,
            (
                round(crop_rect.width * self.TILESET_SCALE),
                round(crop_rect.height * self.TILESET_SCALE),
            ),
        )
        world_position = self.map_point(position)
        rect = image.get_rect(
            topleft=(round(world_position.x), round(world_position.y))
        )
        scaled_collision = None
        if collision_rect is not None:
            scaled_collision = pygame.Rect(
                round(world_position.x + collision_rect[0] * self.TILESET_SCALE),
                round(world_position.y + collision_rect[1] * self.TILESET_SCALE),
                round(collision_rect[2] * self.TILESET_SCALE),
                round(collision_rect[3] * self.TILESET_SCALE),
            )
        if occlusion_y is None:
            occlusion_y = crop_rect.height / 2
        return TilemapObject(
            image,
            rect,
            scaled_collision,
            round(world_position.y + occlusion_y * self.TILESET_SCALE),
        )

    def create_student_npc(self, npc_id, position, ambient_lines):
        """Creates an interactable student with ambient dialogue."""
        return NPC(
            npc_id=npc_id,
            display_name="Estudante",
            position=self.map_point(position),
            sprite_path=(
                "assets/sprites/player/"
                "TheFemaleAdventurer/Idle/Idle_Up.png"
            ),
            dialogue_id="student_smalltalk",
            ambient_lines=ambient_lines,
            use_player_animations=True,
            animation_scale=3,
            interactable=True,
        )

    def get_scene_obstacles(self):
        """Returns map boundaries, object collision, and door rectangles."""
        object_obstacles = (
            obj.collision_rect
            for obj in self.map_objects
            if obj.collision_rect is not None
        )
        return (
            *self.environment_obstacles,
            *object_obstacles,
            *self.get_door_obstacles(),
        )

    def create_laboratory_objects(self):
        """Creates the shared object layout used by both laboratory scenes."""
        objects = [
            self.create_map_object(
                "assets/tileset/scene_objects/mesa_prof.png",
                (44, 110),
                collision_rect=(4, 53, 91, 25),
                occlusion_y=62,
            )
        ]
        objects.extend(
            self.create_map_object(
                "assets/tileset/scene_objects/Vaso.png",
                position,
                collision_rect=(13, 54, 34, 20),
                occlusion_y=60,
            )
            for position in (
                (913, 119),
                (913, 190),
                (913, 262),
                (913, 335),
                (913, 478),
                (913, 551),
            )
        )
        for position, obstacle in LABORATORY_FURNITURE:
            objects.append(
                self.create_map_object(
                    "assets/tileset/scene_objects/mesa_computador_cadeira.png",
                    position,
                    collision_rect=(
                        obstacle[0] - position[0],
                        obstacle[1] - position[1],
                        obstacle[2],
                        obstacle[3],
                    ),
                    occlusion_y=60,
                )
            )
        return objects

    def draw_scene_entities(self, surface, npc_group):
        """Draws characters and props in depth order using their foot hitboxes."""
        drawables = [
            (
                get_entity_hitbox(entity).top,
                1,
                entity.image,
                entity.rect,
            )
            for entity in (*tuple(npc_group), self.player)
        ]
        drawables.extend(
            (obj.occlusion_y, 0, obj.image, obj.rect)
            for obj in self.map_objects
        )
        for _, _, image, rect in sorted(drawables, key=lambda item: item[:2]):
            surface.blit(image, rect)

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


class TilemapObject:
    """A sprite positioned in the map with collision and depth metadata."""

    def __init__(self, image, rect, collision_rect, occlusion_y):
        self.image = image
        self.rect = rect
        self.collision_rect = collision_rect
        self.occlusion_y = occlusion_y

    def should_draw_in_front_of(self, entity):
        """Uses the top of the entity's leg hitbox as its depth reference."""
        return get_entity_hitbox(entity).top < self.occlusion_y
