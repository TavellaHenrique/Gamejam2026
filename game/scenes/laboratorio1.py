import pygame

from game.entities.door import Door
from game.entities.npc import NPC
from game.items.item import Item
from game.scenes.saguao import Saguao
from game.systems.npc_controller import NPCController
from game.systems.quests.quest_status import QuestStatus
from game.systems.tilemap_scene import LABORATORY_OBSTACLES, TilemapScene


class Laboratorio1(TilemapScene):
    """Laboratório de exploração com o Professor Adriano e seus alunos."""

    REFERENCE_WIDTH = 2400
    REFERENCE_HEIGHT = 1400

    @classmethod
    def _fit_tileset_point(cls, position):
        """Maps the reference scene layout onto the enlarged tileset."""
        world_width = round(960 * cls.TILESET_SCALE)
        world_height = round(640 * cls.TILESET_SCALE)
        return (
            round(position[0] * world_width / cls.REFERENCE_WIDTH),
            round(position[1] * world_height / cls.REFERENCE_HEIGHT),
        )

    def __init__(self, game):
        spawn = self._fit_tileset_point((1000, 875))
        super().__init__(
            game,
            "assets/tileset/laboratorio/laboratorio_base.jpg",
            player_spawn=spawn,
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
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            28,
        )
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            22,
        )

        self.npc_controller = NPCController(
            game,
            npcs=(
                NPC(
                    npc_id="professor_lab1",
                    display_name="Professor Adriano",
                    position=self._fit_tileset_point((2000, 700)),
                    sprite_path="assets/sprites/npcs/character3.png",
                    dialogue_id="adriano_lab1_1",
                    animation_scale=3,
                    interactable=True,
                ),
                self.create_student_npc(
                    "lab1_student_1",
                    (700, 540),
                ),
                self.create_student_npc(
                    "lab1_student_2",
                    (390, 430),
                ),
                self.create_student_npc(
                    "lab1_student_3",
                    (550, 315),
                ),
                self.create_student_npc(
                    "lab1_student_4",
                    (700, 390),
                ),
                self.create_student_npc(
                    "lab1_walker_1",
                    (390, 545),
                ),
                self.create_student_npc(
                    "lab1_walker_2",
                    (760, 535),
                ),
            ),
            # define o escopo da classe para que o NPCController possa instanciar NPCs dinamicamente
            npc_scope=type(self),
            static_obstacles=self.get_scene_obstacles(),
        )
        self.npc_controller.configure_wandering(
            (
                self.npc_controller.get_npc("lab1_walker_1"),
                self.npc_controller.get_npc("lab1_walker_2"),
            ),
            bounds=self.bounds,
            obstacles=self.get_scene_obstacles(),
        )

    def handle_event(self, event):
        """Encaminha a porta de saída e as interações com NPCs."""
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
                player_spawn=Saguao.map_point((700, 520)),
            )
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
        ):
            nearby_npc = self.npc_controller.get_nearest_interactable_npc()
            if nearby_npc is not None and nearby_npc.npc_id == "professor_lab1":
                if (
                    self.game.quest_manager.get_status("find_the_key")
                    == QuestStatus.ACTIVE
                    and not self.player.inventory.has_item("lab_key")
                ):
                    nearby_npc.dialogue_id = (
                        "adriano_missao_encontrar_chave"
                    )
                elif "investigation_unlocked" in self.game.story_flags:
                    nearby_npc.dialogue_id = "adriano_missao_chaveiro"
                else:
                    nearby_npc.dialogue_id = "adriano_lab1_1"

        was_adriano_giving_key = (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and self.game.dialogue_manager.is_active
            and self.npc_controller.active_dialogue_npc is not None
            and self.npc_controller.active_dialogue_npc.npc_id
            == "professor_lab1"
            and self.npc_controller.active_dialogue_npc.dialogue_id
            == "adriano_missao_encontrar_chave"
        )
        self.npc_controller.handle_event(event)
        if (
            was_adriano_giving_key
            and not self.game.dialogue_manager.is_active
            and self.game.quest_manager.get_status("find_the_key")
            == QuestStatus.ACTIVE
            and not self.player.inventory.has_item("lab_key")
        ):
            key = Item(
                item_id="lab_key",
                name="Chave do Lab 7",
                description="Chave comum",
                image_path="assets/sprites/items/vecteezy_key-pixel-icon.png"
            )
            if self.player.inventory.add_item(key):
                self.game.register_quest_event("collect_item", key.id)

    def update(self, delta_time):
        """Atualiza a câmera, os NPCs e o jogador."""
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
        """Desenha o mundo em coordenadas absolutas e a interface na viewport."""
        world = self.begin_world_draw()
        self.draw_scene_entities(world, self.npc_controller.npcs)
        self.render_world(screen)
        self.npc_controller.draw_ui(screen, camera=self.camera)
        title = self.title_font.render(
            "Laboratório 1",
            True,
            (255, 255, 255),
        )
        screen.blit(title, (18, 14))
        self.draw_door_hint(
            screen,
            self.hint_font,
            self.player,
            self.doors,
            dialogue_manager=self.game.dialogue_manager,
        )
