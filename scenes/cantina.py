"""Cena da cantina ambientada no tileset correspondente."""

import pygame

from entities.door import Door
from entities.npc import NPC
from scenes.saguao import Saguao
from systems.npc_controller import NPCController
from systems.tilemap_scene import TilemapScene


class Cantina(TilemapScene):
    """Cantina com estudantes estáticos e câmera seguindo o jogador."""

    def __init__(self, game, player_spawn=None):
        if player_spawn is None:
            player_spawn = self.map_point((480, 400))
        super().__init__(
            game,
            "assets/tileset/cantina.jpeg",
            player_spawn=player_spawn,
        )
        self.door = Door(
            rect=self.map_rect((895, 10, 48, 84)),
            prompt="Saguão",
            interaction_margin=72,
            visible=False,
        )
        self.doors = (self.door,)
        self.environment_obstacles = tuple(
            self.map_rect(rect)
            for rect in (
                (0, 0, 895, 88),
                (943, 0, 17, 95),
                (22, 115, 418, 85),
                (485, 88, 168, 63),
                (696, 28, 173, 93),
                (48, 277, 95, 106),
                (224, 277, 95, 106),
                (416, 277, 95, 106),
                (608, 277, 95, 106),
                (48, 422, 95, 106),
                (224, 422, 95, 106),
                (416, 422, 95, 106),
                (608, 422, 95, 106),
                (865, 208, 87, 320),
                (72, 585, 31, 40),
                (17, 585, 20, 32),
                (833, 585, 20, 32),
                (888, 585, 31, 40),
            )
        )
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            22,
        )
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            28,
        )
        self.npc_controller = NPCController(
            game,
            npcs=(
                NPC(
                    npc_id=f"cantina_seated_{index}",
                    display_name="",
                    position=self.map_point(position),
                    sprite_path=(
                        "assets/sprites/player/"
                        "TheFemaleAdventurer/Idle/Idle_Up.png"
                    ),
                    dialogue_id="",
                    frame_count=1,
                    scale=3,
                    interactable=False,
                )
                for index, position in enumerate(
                    (
                        (100, 288),
                        (273, 370),
                        (465, 288),
                        (658, 370),
                        (100, 430),
                        (658, 430),
                    ),
                    1,
                )
            ),
            npc_scope=type(self),
            static_obstacles=self.environment_obstacles,
        )

    def handle_event(self, event):
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
            and self.door.can_interact(self.player)
        ):
            self.game.scene_manager.transition_to(
                lambda: Saguao(self.game),
                player_spawn=self.map_point((288, 120)),
            )
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.scene_manager.transition_to(
                lambda: Saguao(self.game),
                player_spawn=self.map_point((288, 120)),
            )
            return
        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        self.camera.follow(self.player)
        self.camera.update(delta_time)
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=self.get_door_obstacles(),
        )
        self.player.update(
            delta_time,
            accept_input=(
                not self.game.dialogue_manager.is_active
                and self.npc_controller.pending_interaction_npc is None
            ),
            bounds=self.bounds,
            obstacles=self.npc_controller.get_player_obstacles(
                self.get_door_obstacles()
            ),
        )

    def draw(self, screen):
        world = self.begin_world_draw()
        self.npc_controller.draw_npcs(world)
        world.blit(self.player.image, self.player.rect)
        self.render_world(screen)
        self.npc_controller.draw_ui(screen, camera=self.camera)

        title = self.title_font.render("Cantina", True, (255, 255, 255))
        screen.blit(title, (24, 20))
        self.draw_door_hint(
            screen,
            self.hint_font,
            self.player,
            self.doors,
        )
        instruction = self.hint_font.render(
            "ESC - Voltar ao saguão",
            True,
            (255, 255, 255),
        )
        screen.blit(
            instruction,
            instruction.get_rect(
                midbottom=(screen.get_width() // 2, screen.get_height() - 18)
            ),
        )
