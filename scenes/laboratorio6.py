"""Laboratório 6 da primeira aula e área de exploração."""

import pygame

from entities.door import Door
from entities.npc import NPC
from systems.cutscene_controller import (
    CutsceneController,
    fade_out,
    npcs,
    dialogue_from_id,
)
from systems.npc_controller import NPCController
from systems.tilemap_scene import LABORATORY_OBSTACLES, TilemapScene


def _create_saguao(game):
    from scenes.saguao import Saguao

    return Saguao(game)


class Laboratorio6(TilemapScene):
    """Laboratório da primeira aula e área de exploração."""

    def __init__(self, game, player_spawn=None):
        """Cria o laboratório, o professor e os alunos da primeira aula."""
        super().__init__(
            game,
            "assets/tileset/laboratorio/laboratorio_base.jpg",
            player_spawn=player_spawn,
        )
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            36,
        )
        self.door = Door(
            rect=self.map_rect((862, 10, 43, 87)),
            prompt="Saguão",
            interaction_margin=72,
            visible=False,
        )
        self.doors = (self.door,)
        self.environment_obstacles = tuple(
            self.map_rect(rect) for rect in LABORATORY_OBSTACLES
        )
        self.map_objects = self.create_laboratory_objects()
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )
        self.npc_controller = NPCController(
            game,
            npcs=[
                NPC(
                    npc_id="thiago",
                    display_name="Professor Thiago",
                    position=self.map_point((700, 160)),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="thiago_lab6_exploration",
                    use_player_animations=True,
                    interactable=True,
                ),
                self.create_student_npc(
                    "lab6_student_1",
                    (700, 550),
                    ("A aula de hoje foi bem interessante.",),
                ),
                self.create_student_npc(
                    "lab6_student_2",
                    (390, 430),
                    ("Vou terminar o trabalho antes de ir embora.",),
                ),
                self.create_student_npc(
                    "lab6_student_3",
                    (700, 390),
                    ("O professor Thiago explicou tudo direitinho.",),
                ),
                self.create_student_npc(
                    "lab6_student_4",
                    (280, 545),
                    ("Preciso entregar esse exercício até amanhã.",),
                ),
            ],
            npc_scope=type(self),
            static_obstacles=self.get_scene_obstacles(),
        )
        class_actions = [dialogue_from_id("thiago_lab6_roll_call")]
        student_destinations = {
            "lab6_student_1": self.map_point((775, 125)),
            "lab6_student_2": self.map_point((820, 125)),
            "lab6_student_3": self.map_point((865, 125)),
            "lab6_student_4": self.map_point((910, 125)),
        }
        class_actions.append(npcs(student_destinations))
        for student_id in student_destinations:
            class_actions.append(fade_out(student_id, duration=0.25))
        class_actions.append(dialogue_from_id("first_day_lab6_thought"))
        self.cutscene_controller = CutsceneController.create_story_cutscene(
            game,
            self.npc_controller,
            *class_actions,
            cutscene_id="first_day_lab6_class",
            bounds=self.bounds,
            camera=self.camera,
        )
        self.cutscene_controller.start()

    def handle_event(self, event):
        """Avança diálogos e inicia o retorno ao interagir com a porta."""
        if self.is_inventory_open():
            return
        if self.cutscene_controller.handle_event(event):
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
            and not self.cutscene_controller.locks_player_control
            and self.door.can_interact(self.player)
        ):
            self.game.scene_manager.transition_to(
                lambda: _create_saguao(self.game),
                player_spawn=self.map_point((900, 150)),
            )
            return

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Atualiza a aula, a câmera, os NPCs e o jogador."""
        self.update_camera(delta_time, self.cutscene_controller)
        self.cutscene_controller.update(delta_time)
        self.player.update(
            delta_time,
            accept_input=(
                # Diálogos, cutscene e inventário bloqueiam o controle do jogador.
                not self.game.inventory_open
                and not self.game.dialogue_manager.is_active
                and not self.cutscene_controller.locks_player_control
                # A aproximação automática à conversa controla o jogador.
                and not self.npc_controller.interaction_cutscene.is_active
                # O jogador não deve se mover enquanto está sendo posicionado.
                and not self.npc_controller.is_approaching_npc
                # Uma interação pendente ainda está preparando a conversa.
                and self.npc_controller.pending_interaction_npc is None
            ),
            bounds=self.bounds,
            obstacles=self.npc_controller.get_player_obstacles(
                self.get_door_obstacles()
            ),
        )
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=self.get_door_obstacles(),
        )

    def draw(self, screen):
        """Desenha o tileset, os personagens e a interface."""
        world = self.begin_world_draw()
        self.draw_scene_entities(world, self.npc_controller.npcs)
        self.render_world(screen)

        title = self.title_font.render(
            "Laboratório",
            True,
            (255, 255, 255),
        )
        screen.blit(title, (24, 20))

        self.draw_door_hint(
            screen,
            self.hint_font,
            self.player,
            self.doors,
            dialogue_manager=self.game.dialogue_manager,
        )
        self.npc_controller.draw_ui(screen, camera=self.camera)
