"""Shared camera and rendering setup for scenes backed by a tileset image."""

import math
import sys
from pathlib import Path

import pygame

from game.config import SCREEN_HEIGHT, SCREEN_WIDTH
from game.entities.npc import NPC
from game.scenes.scene import Scene
from game.systems.camera_manager import CameraManager
from game.systems.collision import get_entity_hitbox
from game.systems.objects_collision import create_object_collision
from game.ui.text import draw_prompt


LABORATORY_OBSTACLES = (
    (0, 0, 862, 96),
    (905, 0, 55, 96),
    (0, 96, 14, 529),
    (946, 96, 14, 529),
    (14, 625, 932, 15),
)

LABORATORY_FURNITURE = (
    (52, 205),
    (164, 205),
    (268, 205),
    (452, 205),
    (580, 205),
    (52, 317),
    (180, 317),
    (292, 317),
    (452, 317),
    (580, 317),
    (52, 429),
    (180, 429),
    (293, 437),
    (452, 429),
    (580, 429),
)

STUDENT_SPRITES = (
    "assets/sprites/npcs/Blue_Head_Idle-Sheet.png",
    "assets/sprites/npcs/Pink_Head_Idle-Sheet.png",
)


class TilemapScene(Scene):
    """Scene base that scales a background image and shows one map quadrant."""

    TILESET_SCALE = 1.2 # Scale factor for the tileset image to world coordinates.
    CAMERA_ZOOM_FACTOR = 0.38 # Scale factor for the camera zoom to fit one quadrant of the tileset.
    DIALOGUE_CAMERA_TRANSITION_DURATION = 1.0
    _object_image_cache = {}
    _example_image_cache = {}

    def __init__(self, game, tileset_path, player_spawn=None):
        super().__init__(game)
        self.player = game.player
        self._student_sprite_index = 0
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
        self._camera_follow_target = self.player
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
        collidable=False,
        occlusion_y=None,
    ):
        """Creates a prop with optional collision matching its sprite bounds."""
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
        scaled_collision = self._create_object_collision(
            rect,
            collidable,
            image_path,
        )

        if occlusion_y is None:
            occlusion_y = image.get_height() / self.TILESET_SCALE / 2
        source_location = self._format_source_location(sys._getframe(1))
        return TilemapObject(
            image,
            rect,
            scaled_collision,
            round(world_position.y + occlusion_y * self.TILESET_SCALE),
            name=image_path.replace("\\", "/").rsplit("/", 1)[-1],
            source_location=source_location,
        )

    def create_map_object_from_example(
        self,
        example_path,
        crop_rect,
        position,
        collidable=False,
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
        scaled_collision = self._create_object_collision(
            rect,
            collidable,
            example_path,
        )
        if occlusion_y is None:
            occlusion_y = crop_rect.height / 2
        source_location = self._format_source_location(sys._getframe(1))
        return TilemapObject(
            image,
            rect,
            scaled_collision,
            round(world_position.y + occlusion_y * self.TILESET_SCALE),
            name=example_path.replace("\\", "/").rsplit("/", 1)[-1],
            source_location=source_location,
        )

    def _create_object_collision(self, object_rect, collidable, image_path):
        """Uses the configured collision area without automatic centering."""
        if not collidable:
            return None

        return create_object_collision(object_rect, image_path)

    @staticmethod
    def _format_source_location(frame):
        source_path = Path(frame.f_code.co_filename).resolve()
        project_root = Path(__file__).resolve().parent.parent
        try:
            source_path = source_path.relative_to(project_root)
        except ValueError:
            pass
        return f"{source_path.as_posix()}:{frame.f_lineno}"

    def create_student_npc(self, npc_id, position):
        """Creates an interactable student with ambient dialogue."""
        sprite_path = STUDENT_SPRITES[
            self._student_sprite_index % len(STUDENT_SPRITES)
        ]
        self._student_sprite_index += 1
        return NPC(
            npc_id=npc_id,
            display_name="Estudante",
            position=self.map_point(position),
            sprite_path=sprite_path,
            dialogue_id="student_smalltalk",
            ambient_lines=self.game.dialogue_manager.get_lines(
                "falas_aleatorias"
            ),
            use_player_animations=False,
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
                collidable=True,
                occlusion_y=62,
            )
        ]
        objects.extend(
            self.create_map_object(
                "assets/tileset/scene_objects/Vaso.png",
                position,
                collidable=True,
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
        for position in LABORATORY_FURNITURE:
            objects.append(
                self.create_map_object(
                    "assets/tileset/scene_objects/mesa_computador_cadeira.png",
                    position,
                    collidable=True,
                    occlusion_y=60,
                )
            )
        return objects

    def draw_scene_entities(self, surface, npc_group):
        """Draws sprites in world Y order using the bottom of their hitboxes."""
        drawables = [
            (
                get_entity_hitbox(entity).bottom,
                entity.image,
                entity.rect,
            )
            for entity in (*tuple(npc_group), self.player)
        ]
        drawables.extend(
            (
                (
                    obj.collision_rect
                    if obj.collision_rect is not None
                    else obj.rect
                ).bottom,
                obj.image,
                obj.rect,
            )
            for obj in self.map_objects
        )

        for _, image, rect in sorted(drawables, key=lambda drawable: drawable[0]):
            surface.blit(image, rect)

    def update_camera(self, delta_time, cutscene_controller):
        """Follows the dialogue speaker, or the player outside dialogue."""
        if (
            cutscene_controller is not None
            and cutscene_controller.waiting_for == "camera_movement"
        ):
            return

        target = self.player
        if self.game.dialogue_manager.is_active:
            target = self.npc_controller.get_dialogue_speaker() or self.player

        if target is not self._camera_follow_target:
            self.camera.move_to(
                target.position,
                duration=self.DIALOGUE_CAMERA_TRANSITION_DURATION,
            )
            self._camera_follow_target = target

        self.camera.follow(target)
        self.camera.update(delta_time)

    def begin_world_draw(self):
        """Returns the camera surface with the enlarged tileset background."""
        self.camera.world_surface.blit(self.map_image, (0, 0))
        return self.camera.world_surface

    def render_world(self, screen):
        """Renders the camera's current map region onto the game window."""
        self.camera.render(screen)

    def get_debug_info(self, screen_position):
        """Returns world coordinates and details for the object under the cursor."""
        render_rect = self.camera.render_rect
        if not render_rect.collidepoint(screen_position):
            return ["Mouse fora da área renderizada."]

        world_position = self.camera.screen_to_world(screen_position)
        lines = [
            f"Mundo X: {world_position.x:.1f}  Y: {world_position.y:.1f}"
        ]
        target = self._get_debug_target(world_position)
        if target is not None:
            lines.extend(target["details"])
        else:
            lines.append("Alvo: nenhum")
        return lines

    def draw_debug_geometry(self, screen):
        """Highlights entity hitboxes, props, and collision rectangles."""
        for target in self._get_debug_targets():
            for rect in target["outlines"]:
                pygame.draw.rect(
                    screen,
                    target["color"],
                    self._world_rect_to_screen(rect),
                    width=2,
                )

    def print_debug_target(self, screen_position):
        """Prints the clicked object details in the terminal."""
        render_rect = self.camera.render_rect
        if not render_rect.collidepoint(screen_position):
            print("DEBUG: clique fora da área renderizada.")
            return

        world_position = self.camera.screen_to_world(screen_position)
        target = self._get_debug_target(world_position)
        if target is None:
            print(
                "DEBUG: nenhum alvo em "
                f"X={world_position.x:.1f}, Y={world_position.y:.1f}"
            )
            return

        print(
            f"DEBUG: clique em X={world_position.x:.1f}, "
            f"Y={world_position.y:.1f} - {target['name']}"
        )
        for detail in target["details"]:
            print(f"  {detail}")

    def _get_debug_target(self, world_position):
        for target in self._get_debug_targets():
            if target["rect"].collidepoint(world_position):
                return target
        return None

    def _get_debug_targets(self):
        targets = []
        npc_controller = getattr(self, "npc_controller", None)
        if npc_controller is not None:
            for npc in npc_controller.npcs:
                hitbox = get_entity_hitbox(npc)
                targets.append(
                    self._make_debug_target(
                        "NPC",
                        f"NPC {npc.display_name} ({npc.npc_id})",
                        npc.position,
                        npc.rect,
                        (npc.rect, hitbox),
                        (100, 220, 255),
                        f"Hitbox: {self._rect_details(hitbox)}",
                        f"Sprite: {self._rect_details(npc.rect)}",
                    )
                )

        player_hitbox = get_entity_hitbox(self.player)
        targets.append(
            self._make_debug_target(
                "Jogador",
                "Jogador",
                self.player.position,
                self.player.rect,
                (self.player.rect, player_hitbox),
                (100, 255, 140),
                f"Hitbox: {self._rect_details(player_hitbox)}",
                f"Sprite: {self._rect_details(self.player.rect)}",
            )
        )

        for index, obj in enumerate(getattr(self, "map_objects", ())):
            name = getattr(obj, "name", f"Objeto do mapa {index + 1}")
            outlines = [obj.rect]
            collision_rect = getattr(obj, "collision_rect", None)
            extra = []
            if collision_rect is not None:
                outlines.append(collision_rect)
                extra.append(
                    f"Colisão: {self._rect_details(collision_rect)}"
                )
                extra.append(
                    f"Colisão definida em: {obj.source_location}"
                )
            extra.append(f"Objeto criado em: {obj.source_location}")
            targets.append(
                self._make_debug_target(
                    "Objeto",
                    name,
                    obj.rect.topleft,
                    (
                        obj.rect.union(collision_rect)
                        if collision_rect is not None
                        else obj.rect
                    ),
                    tuple(outlines),
                    (255, 210, 90),
                    *extra,
                )
            )

        for item in getattr(self, "items", ()):
            if not item.visible:
                continue
            if item.world_image is not None:
                rect = item.world_image.get_rect(
                    center=(round(item.position.x), round(item.position.y))
                )
            else:
                radius = round(item.interaction_radius)
                rect = pygame.Rect(
                    round(item.position.x) - radius,
                    round(item.position.y) - radius,
                    radius * 2,
                    radius * 2,
                )
            targets.append(
                self._make_debug_target(
                    "Objeto",
                    f"Item {item.name} ({item.item_id})",
                    item.position,
                    rect,
                    (rect,),
                    (255, 180, 100),
                )
            )

        object_collisions = {
            tuple(obj.collision_rect)
            for obj in getattr(self, "map_objects", ())
            if obj.collision_rect is not None
        }
        seen_collisions = set()
        for index, obstacle in enumerate(self.get_scene_obstacles()):
            rect = pygame.Rect(obstacle)
            key = tuple(rect)
            if key in object_collisions or key in seen_collisions:
                continue
            seen_collisions.add(key)
            targets.append(
                self._make_debug_target(
                    "Colisão",
                    f"Colisão de cenário {index + 1}",
                    rect.center,
                    rect,
                    (rect,),
                    (255, 100, 100),
                )
            )

        return targets

    def _make_debug_target(
        self,
        kind,
        name,
        position,
        hit_rect,
        outlines,
        color,
        *extra_details,
    ):
        position = pygame.Vector2(position)
        details = [
            f"Tipo: {kind}",
            f"Nome: {name}",
            f"Posição: X={position.x:.1f}, Y={position.y:.1f}",
            f"Área: {self._rect_details(hit_rect)}",
            *extra_details,
        ]
        return {
            "kind": kind,
            "name": name,
            "rect": hit_rect,
            "outlines": outlines,
            "color": color,
            "details": details,
        }

    @staticmethod
    def _rect_details(rect):
        return (
            f"X={rect.x}, Y={rect.y}, "
            f"Largura={rect.width}, Altura={rect.height}"
        )

    def _world_rect_to_screen(self, rect):
        top_left = self.camera.world_to_screen(rect.topleft)
        bottom_right = self.camera.world_to_screen(rect.bottomright)
        return pygame.Rect(
            round(top_left.x),
            round(top_left.y),
            max(1, round(bottom_right.x - top_left.x)),
            max(1, round(bottom_right.y - top_left.y)),
        )

    @staticmethod
    def draw_door_hint(
        screen,
        font,
        player,
        doors,
        prefix="E - ",
        dialogue_manager=None,
    ):
        """Shows an interaction hint for the nearest active transparent door."""
        for door in doors:
            if not door.can_interact(player):
                continue

            draw_prompt(
                screen,
                f"{prefix}{door.prompt}",
                font,
                dialogue_manager=dialogue_manager,
            )
            return


class TilemapObject:
    """A sprite positioned in the map with collision and depth metadata."""

    def __init__(
        self,
        image,
        rect,
        collision_rect,
        occlusion_y,
        name=None,
        source_location=None,
    ):
        self.image = image
        self.rect = rect
        self.collision_rect = collision_rect
        self.occlusion_y = occlusion_y
        self.name = name or "Objeto do mapa"
        self.source_location = source_location or "Origem desconhecida"
