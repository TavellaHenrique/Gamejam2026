"""Cena da cantina ambientada no tileset correspondente."""

import pygame

from game.entities.door import Door
from game.scenes.saguao import Saguao
from game.systems.npc_controller import NPCController
from game.systems.tilemap_scene import TilemapScene
from game.systems.quests.quest_status import QuestStatus
from game.systems.trigger import Trigger
from game.ui.text import draw_prompt


class Cantina(TilemapScene):
    """Cantina com estudantes estáticos e câmera seguindo o jogador."""

    def __init__(self, game, player_spawn=None):
        if player_spawn is None:
            player_spawn = self.map_point((480, 400))
        super().__init__(
            game,
            "assets/tileset/cantina/cantina_base.jpg",
            player_spawn=player_spawn,
        )
        self.door = Door(
            rect=self.map_rect((895, 10, 48, 84)),
            prompt="Saguão",
            interaction_margin=72,
            visible=False,
        )
        self.doors = (self.door,)
        self.vending_machine_trigger = Trigger(
            position=self.map_point((730, 145)),
            radius=80,
        )
        self.environment_obstacles = tuple(
            self.map_rect(rect)
            for rect in (
                (0, 0, 895, 88),
                (943, 0, 17, 95),
                (865, 208, 87, 320),
            )
        )
        self.map_objects = [
            self.create_map_object(
                "assets/tileset/scene_objects/mesa_refeitorio.png",
                (0, 113),
                collidable=True,
                occlusion_y=70,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/mesa_refeitorio.png",
                (205, 113),
                collidable=True,
                occlusion_y=70,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/pia.png",
                (484, 82),
                collidable=True,
                occlusion_y=45,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/pia.png",
                (580, 82),
                collidable=True,
                occlusion_y=45,
            ),
            *(
                self.create_map_object(
                    "assets/tileset/scene_objects/lixeira.png",
                    position,
                    collidable=True,
                    occlusion_y=16,
                )
                for position in ((541, 88), (637, 88))
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/Maquina_verde.png",
                (695, 26),
                collidable=True,
                occlusion_y=65,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/maquina_roxa.png",
                (761, 30),
                collidable=True,
                occlusion_y=65,
            ),
            *(
                self.create_map_object(
                    "assets/tileset/scene_objects/lixeira.png",
                    position,
                    collidable=True,
                    occlusion_y=16,
                )
                for position in ((17, 585), (833, 585))
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/maquina_roxa.png",
                (831, 30),
                collidable=True,
                occlusion_y=65,
            ),
            *(
                self.create_map_object(
                    "assets/tileset/scene_objects/mesa_cadeira.png",
                    position,
                    collidable=True,
                    occlusion_y=55,
                )
                for position in (
                    (48, 277),
                    (224, 277),
                    (416, 277),
                    (608, 277),
                    (48, 422),
                    (224, 422),
                    (416, 422),
                    (608, 422),
                )
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/Vaso.png",
                (74, 550),
                collidable=True,
                occlusion_y=60,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/Vaso.png",
                (888, 550),
                collidable=True,
                occlusion_y=60,
            ),
        ]
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
                self.create_student_npc(
                    "cantina_student_1",
                    (170, 340),
                ),
                self.create_student_npc(
                    "cantina_student_2",
                    (350, 340),
                ),
                self.create_student_npc(
                    "cantina_student_3",
                    (540, 340),
                ),
                self.create_student_npc(
                    "cantina_student_4",
                    (750, 340),
                ),
                self.create_student_npc(
                    "cantina_walker_1",
                    (350, 220),
                ),
                self.create_student_npc(
                    "cantina_walker_2",
                    (780, 220),
                ),
                self.create_student_npc(
                    "cantina_walker_3",
                    (450, 560),
                ),
            ),
            npc_scope=type(self),
            static_obstacles=self.get_scene_obstacles(),
        )
        self.npc_controller.configure_wandering(
            (
                self.npc_controller.get_npc("cantina_walker_1"),
                self.npc_controller.get_npc("cantina_walker_2"),
                self.npc_controller.get_npc("cantina_walker_3"),
            ),
            bounds=self.bounds,
            obstacles=self.get_scene_obstacles(),
        )

    def handle_event(self, event):
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
            and self.game.quest_manager.get_status("eat_snacks")
            == QuestStatus.ACTIVE
            and self.vending_machine_trigger.contains(self.player)
        ):
            self.game.register_quest_event(
                "interact_with",
                "cantina_vending_machine",
            )
            self.npc_controller.start_monologue("passando_mal_salgadinho")
            return

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

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        self.update_camera(delta_time, None)
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=(),
        )
        self.player.update(
            delta_time,
            accept_input=(
                not self.game.dialogue_manager.is_active
                and self.npc_controller.pending_interaction_npc is None
            ),
            bounds=self.bounds,
            obstacles=self.npc_controller.get_player_obstacles(),
        )

    def draw(self, screen):
        world = self.begin_world_draw()
        self.draw_scene_entities(world, self.npc_controller.npcs)
        self.render_world(screen)
        self.npc_controller.draw_ui(screen, camera=self.camera)

        title = self.title_font.render("Cantina", True, (255, 255, 255))
        screen.blit(title, (24, 20))
        self.draw_door_hint(
            screen,
            self.hint_font,
            self.player,
            self.doors,
            dialogue_manager=self.game.dialogue_manager,
        )
        if (
            self.game.quest_manager.get_status("eat_snacks")
            == QuestStatus.ACTIVE
            and self.vending_machine_trigger.contains(self.player)
        ):
            draw_prompt(
                screen,
                "E - Comprar salgadinho",
                self.hint_font, # type: ignore
                dialogue_manager=self.game.dialogue_manager,
            )
