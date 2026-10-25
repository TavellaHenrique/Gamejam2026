import pygame

from game.entities.door import Door
from game.entities.elevator import Elevator
from game.entities.npc import NPC
from game.scenes.laboratorio6 import Laboratorio6
from game.systems.cutscene_controller import (
    CutsceneController,
    change_scene,
    fade_out,
    npc,
    npcs,
    player_destination,
    dialogue_from_id,
)
from game.systems.npc_controller import NPCController
from game.systems.quests.quest_status import QuestStatus
from game.systems.tilemap_scene import TilemapScene


class Saguao(TilemapScene):
    """Saguão da história inicial e área livre para exploração."""

    def __init__(self, game, player_spawn=None):
        """Configura o jogador compartilhado e os NPCs da cena."""
        if (
            player_spawn is None
            and not game.is_cutscene_completed("first_day_saguao")
        ):
            player_spawn = self.map_point((700, 100))
        super().__init__(
            game,
            "assets/tileset/saguao/saguao_base.jpg",
            player_spawn=player_spawn,
        )
        self.player = game.player
        self.cantina_door = Door(
            rect=self.map_rect((230, 0, 116, 95)),
            prompt="Cantina",
            interaction_margin=72,
            visible=False,
        )
        self.lab_door = Door(
            rect=self.map_rect((875, 10, 47, 86)),
            prompt="Laboratório 6",
            interaction_margin=72,
            visible=False,
        )
        self.elevator = Elevator(
            rect=self.map_rect((0, 442, 64, 116)),
            destinations=(
                ("lab1", "Laboratório 1"),
                ("lab6", "Laboratório 6"),
                ("professora_lab", "Laboratório 8"),
                ("cancel", "Cancelar"),
            ),
        )
        self.elevator_door = self.elevator.door
        self.stairs_door = Door(
            rect=self.map_rect((750, 430, 200, 195)),
            prompt="Laboratório 1",
            interaction_margin=72,
            visible=False,
        )
        self.door = self.lab_door
        self.doors = (
            self.cantina_door,
            self.lab_door,
            self.elevator_door,
            self.stairs_door,
        )
        stair_obstacles = []
        for top in range(430, 640, 16):
            left = max(750, 960 - (top + 16 - 430))
            stair_obstacles.append((left, top, 960 - left, 16))

        self.environment_obstacles = tuple(
            self.map_rect(rect)
            for rect in (
                (0, 0, 230, 96),
                (346, 0, 529, 96),
                (922, 0, 38, 96),
                *stair_obstacles,
            )
        )
        self.map_objects = [
            *(
                self.create_map_object_from_example(
                    "assets/tileset/saguao/saguao_exemplo.jpeg",
                    (x, y, 24, 72),
                    (x, y),
                    collidable=True,
                    occlusion_y=36,
                )
                for x, y in (
                    (55, 205),
                    (290, 205),
                    (738, 205),
                    (55, 300),
                    (290, 300),
                    (738, 284),
                )
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/Vaso.png",
                (17, 103),
                collidable=True,
                occlusion_y=60,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/Vaso.png",
                (433, 103),
                collidable=True,
                occlusion_y=60,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/vaso_2.png",
                (18, 566),
                collidable=True,
                occlusion_y=45,
            ),
            *(
                self.create_map_object(
                    "assets/tileset/scene_objects/banco.png",
                    (x, y),
                    collidable=True,
                    occlusion_y=16,
                )
                for x, y in (
                    (89, 165),
                    (185, 165),
                    (505, 165),
                    (617, 165),
                    (89, 381),
                    (505, 334),
                    (601, 334),
                )
            ),
        ]
        self.map_objects.extend(
            self.create_map_object(
                "assets/tileset/scene_objects/lixeira.png",
                position,
                collidable=True,
                occlusion_y=16,
            )
            for position in ((12, 376), (412, 344))
        )
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )
        self.npc_controller = NPCController(
            game,
            npcs=[
                NPC(
                    npc_id="professor_thiago_saguao",
                    display_name="Professor Thiago",
                    position=self.map_point((720, 400)),
                    sprite_path="assets/sprites/npcs/character1.png",
                    dialogue_id="thiago_welcome",
                    interactable=False,
                ),
                self.create_student_npc(
                    "saguao_student_1",
                    (125, 215),
                ),
                self.create_student_npc(
                    "saguao_student_2",
                    (220, 215),
                ),
                NPC(
                    npc_id="weird_girl",
                    display_name="Garota Estranha",
                    position=self.map_point((545, 215)),
                    sprite_path=(
                        "assets/sprites/npcs/Orange_Head_Idle-Sheet.png"
                    ),
                    dialogue_id="weird_girl_introduction",
                    animation_scale=3,
                ),
                self.create_student_npc(
                    "saguao_student_4",
                    (690, 380),
                ),
                self.create_student_npc(
                    "saguao_walker_1",
                    (365, 410),
                ),
                self.create_student_npc(
                    "saguao_walker_2",
                    (680, 500),
                ),
            ],
            npc_scope=type(self),
            static_obstacles=self.get_scene_obstacles(),
        )
        self.npc_controller.configure_wandering(
            (
                self.npc_controller.get_npc("saguao_walker_1"),
                self.npc_controller.get_npc("saguao_walker_2"),
            ),
            bounds=self.bounds,
            obstacles=self.get_scene_obstacles(),
        )
        self.aluna_thought_pending = False
        self.cutscene_controller = CutsceneController.create_story_cutscene(
            game,
            self.npc_controller,
            dialogue_from_id("first_day_saguao_intro"),
            dialogue_from_id("thiago_welcome"),
            npc(
                "professor_thiago_saguao",
                self.map_point((900, 100)),
            ),
            fade_out("professor_thiago_saguao", duration=0.25),
            npcs(
                {
                    "saguao_student_1": self.map_point((800, 45)),
                    "saguao_student_2": self.map_point((850, 45)),
                    "saguao_student_4": self.map_point((900, 45)),
                }
            ),
            fade_out("saguao_student_1", duration=0.25),
            fade_out("saguao_student_2", duration=0.25),
            fade_out("saguao_student_4", duration=0.25),
            player_destination(self.map_point((900, 100))),
            change_scene(
                lambda: Laboratorio6(game),
                player_spawn=Laboratorio6.map_point((600, 320)),
            ),
            cutscene_id="first_day_saguao",
            bounds=self.bounds,
            camera=self.camera,
        )
        self.cutscene_controller.start()

    def handle_event(self, event):
        """Delega falas da história e encaminha interações da cena."""
        if self.elevator.is_open:
            _, destination = self.elevator.handle_event(event, self.player)
            if destination is not None:
                self._travel_to_elevator_destination(destination)
            return

        if self.is_inventory_open():
            return

        if self.cutscene_controller.handle_event(event):
            return

        if (
            not self.game.dialogue_manager.is_active
            and not self.cutscene_controller.locks_player_control
        ):
            consumed, destination = self.elevator.handle_event(
                event,
                self.player,
            )
            if consumed:
                return

        aluna = self.npc_controller.get_npc("weird_girl")
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and self.game.dialogue_manager.is_active
            and self.npc_controller.pending_interaction_npc is aluna
        ):
            is_introduction_dialogue = (
                aluna.dialogue_id == "weird_girl_introduction"
            )
            self.npc_controller.handle_event(event)
            if (
                is_introduction_dialogue
                and not self.game.dialogue_manager.is_active
                and self.npc_controller.pending_interaction_npc is None
            ):
                self.aluna_thought_pending = True
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
            and not self.cutscene_controller.locks_player_control
        ):
            nearby_npc = self.npc_controller.get_nearest_interactable_npc()
            if (
                nearby_npc is not None
                and nearby_npc.npc_id == "weird_girl"
                and self.game.quest_manager.get_status("find_the_key")
                == QuestStatus.ACTIVE
            ):
                nearby_npc.dialogue_id = (
                    "garota_estranha_missao_encontrar_chave"
                )
            elif (
                nearby_npc is not None
                and nearby_npc.npc_id == "weird_girl"
                and "investigation_unlocked" in self.game.story_flags
            ):
                nearby_npc.dialogue_id = (
                    "garota_estranha_missao_chaveiro"
                    if self.game.quest_manager.get_status("eat_snacks")
                    == QuestStatus.COMPLETED
                    else "garota_estranha_antes_salgadinho"
                )

            if self.lab_door.can_interact(self.player):
                self.game.scene_manager.transition_to(
                    lambda: Laboratorio6(self.game),
                    player_spawn=self.map_point((800, 150)),
                )
                return

            if self.cantina_door.can_interact(self.player):
                from game.scenes.cantina import Cantina

                self.game.scene_manager.transition_to(
                    lambda: Cantina(self.game),
                    player_spawn=self.map_point((480, 400)),
                )
                return

            if self.stairs_door.can_interact(self.player):
                from game.scenes.laboratorio1 import Laboratorio1

                self.game.scene_manager.transition_to(
                    lambda: Laboratorio1(self.game),
                    player_spawn=Laboratorio1._fit_tileset_point((1000, 875)),
                )
                return

        self.npc_controller.handle_event(event)

    def _travel_to_elevator_destination(self, destination):
        """Transfere o jogador para o destino escolhido no elevador."""
        if destination == "lab6":
            self.game.scene_manager.transition_to(
                lambda: Laboratorio6(self.game),
                player_spawn=self.map_point((800, 150)),
            )
        elif destination == "lab1":
            from game.scenes.laboratorio1 import Laboratorio1

            self.game.scene_manager.transition_to(
                lambda: Laboratorio1(self.game),
                player_spawn=Laboratorio1._fit_tileset_point((800, 100)),
            )
        elif destination == "professora_lab":
            from game.scenes.laboratorio_professora import LaboratorioProfessora

            self.game.scene_manager.transition_to(
                lambda: LaboratorioProfessora(self.game),
                player_spawn=LaboratorioProfessora.map_point((800, 150)),
            )

    def update(self, delta_time):
        """Atualiza a história, os NPCs, os itens e o jogador."""
        self.update_camera(delta_time, self.cutscene_controller)
        self.cutscene_controller.update(delta_time)
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=(),
        )
        aluna = self.npc_controller.get_npc("weird_girl")
        if (
            self.aluna_thought_pending
            and not self.game.dialogue_manager.is_active
            and self.player.position.distance_to(aluna.position)
            > aluna.interaction_radius + 40
        ):
            self.game.dialogue_manager.start("though_about_weird_girl")
            self.aluna_thought_pending = False

        self.player.update(
            delta_time,
            accept_input=(
                # Diálogos, cutscene e inventário bloqueiam o controle para não andar durante as falas.
                not self.game.inventory_open
                and not self.game.dialogue_manager.is_active
                # A cutscene bloqueia o teclado, exceto enquanto aguarda o gatilho.
                and not self.cutscene_controller.locks_player_control
                # A aproximação automática à conversa controla o jogador.
                and not self.npc_controller.interaction_cutscene.is_active
                # O jogador não deve se mover enquanto está sendo posicionado.
                and not self.npc_controller.is_approaching_npc
                # Uma interação pendente ainda está preparando a conversa.
                and self.npc_controller.pending_interaction_npc is None
            ),
            bounds=self.bounds,
            obstacles=self.npc_controller.get_player_obstacles(),
        )

    def draw(self, screen):
        """Desenha o fundo, personagens e interface da cena."""
        world = self.begin_world_draw()
        self.elevator.draw_world(world, self.player)
        self.draw_scene_entities(world, self.npc_controller.npcs)
        self.render_world(screen)

        self.draw_door_hint(
            screen,
            self.hint_font,
            self.player,
            (
                self.cantina_door,
                self.lab_door,
                self.stairs_door,
            ),
            dialogue_manager=self.game.dialogue_manager,
        )
        self.npc_controller.draw_ui(screen, camera=self.camera)
        self.elevator.draw_menu(screen)

    @property
    def is_paused(self):
        """Pausa o mundo enquanto o jogador escolhe o destino do elevador."""
        return self.elevator.is_open
