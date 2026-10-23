"""Cena de exploração do laboratório da professora."""

import pygame

from entities.door import Door
from entities.npc import NPC
from scenes.saguao import Saguao
from scenes.laboratorio_professora.layout import (
    create_environment_obstacles,
    create_laboratory_objects,
)
from systems.npc_controller import NPCController
from systems.quests.quest_status import QuestStatus
from systems.tilemap_scene import TilemapScene


class LaboratorioProfessora(TilemapScene):
    """Laboratório da Professora com a missão de busca da chave."""

    def __init__(self, game, player_spawn=None):
        """Monta o cenário, os objetos e as colisões ambientais."""
        super().__init__(
            game,
            "assets/tileset/laboratorio/laboratorio_base.jpg",
            player_spawn=player_spawn,
        )
        self.door = Door(
            rect=self.map_rect((862, 10, 43, 87)),
            prompt="Saguão",
            interaction_margin=72,
            visible=False,
        )
        self.doors = (self.door,)
        self.environment_obstacles = create_environment_obstacles(self)
        self.map_objects = create_laboratory_objects(self)
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            36,
        )
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )
        self.professora = NPC(
            npc_id="professora",
            display_name="Professora",
            position=self.map_point((700, 160)),
            sprite_path="assets/sprites/npcs/Idle_Down.png",
            dialogue_id="professora_introducao",
            use_player_animations=True,
            interactable=True,
        )
        self.npc_controller = NPCController(
            game,
            npcs=(self.professora,),
            npc_scope=type(self),
            static_obstacles=self.get_scene_obstacles(),
        )

    def handle_event(self, event):
        """Encaminha a saída e a conversa que inicia ou conclui a missão."""
        if self.is_inventory_open():
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
            and self.door.can_interact(self.player)
        ):
            self.game.scene_manager.transition_to(
                lambda: Saguao(self.game),
                player_spawn=Saguao.map_point((900, 150)),
            )
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
        ):
            nearby_npc = self.npc_controller.get_nearest_interactable_npc()
            if nearby_npc is self.professora:
                quest_status = self.game.quest_manager.get_status(
                    "find_the_key"
                )
                if quest_status == QuestStatus.AVAIABLE:
                    self.game.quest_manager.start_quest("find_the_key")
                    self.professora.dialogue_id = "professora_introducao"
                elif (
                    quest_status == QuestStatus.ACTIVE
                    and self.player.inventory.has_item("lab_key")
                ):
                    self.professora.dialogue_id = (
                        "professora_chave_devolvida"
                    )
                    self.player.inventory.remove_item("lab_key")
                    self.game.register_quest_event(
                        "return_item",
                        "lab_key",
                    )
                elif quest_status == QuestStatus.ACTIVE:
                    self.npc_controller.start_monologue(
                        "professora_monologo",
                        npc=self.professora,
                    )
                    return
                else:
                    self.professora.dialogue_id = (
                        "professora_chave_devolvida"
                        if quest_status == QuestStatus.COMPLETED
                        else "professora_introducao"
                    )

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Atualiza câmera, professora e jogador com as colisões do laboratório."""
        self.update_camera(delta_time, None)
        player_obstacles = self.npc_controller.get_player_obstacles(
            self.get_door_obstacles()
        )
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=player_obstacles,
        )
        self.player.update(
            delta_time,
            accept_input=(
                not self.game.inventory_open
                and not self.game.dialogue_manager.is_active
                and not self.npc_controller.interaction_cutscene.is_active
                and not self.npc_controller.is_approaching_npc
                and self.npc_controller.pending_interaction_npc is None
            ),
            bounds=self.bounds,
            obstacles=player_obstacles,
        )

    def draw(self, screen):
        """Renderiza o cenário, os objetos ordenados e a interface da cena."""
        world = self.begin_world_draw()
        self.draw_scene_entities(world, self.npc_controller.npcs)
        self.render_world(screen)

        self.npc_controller.draw_ui(screen, camera=self.camera)
        title = self.title_font.render(
            "Laboratório da Professora",
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
