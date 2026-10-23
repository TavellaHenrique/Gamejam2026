import pygame

from entities.door import Door
from entities.npc import NPC
from items.item import Item
from scenes.laboratorio6 import Laboratorio6
from systems.cutscene_controller import (
    CutsceneController,
    change_scene,
    fade_out,
    npc,
    npcs,
    player_destination,
    dialogue_from_id,
)
from systems.npc_controller import NPCController
from systems.tilemap_scene import TilemapScene


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
            prompt="Laboratório",
            interaction_margin=72,
            visible=False,
        )
        self.elevator_door = Door(
            rect=self.map_rect((0, 442, 64, 116)),
            prompt="Elevador",
            interaction_margin=72,
            visible=False,
        )
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
        self.items = [
            Item(
                item_id="lab_key",
                name="Chave do laboratório",
                description="O professor vai pedir isso na história.",
                position=self.map_point((620, 420)),
                interaction_radius=54,
            ),
            Item(
                item_id="battery",
                name="Bateria",
                description="Um pequeno dispositivo de energia.",
                position=self.map_point((780, 260)),
                interaction_radius=45,
            ),
            Item(
                item_id="note",
                name="Bilhete",
                description="Mensagem antiga do laboratório.",
                position=self.map_point((320, 560)),
                interaction_radius=48,
            ),
        ]
        for item in self.items:
            if self.player.inventory.has_item(item.id):
                item.collected = True
                item.visible = False
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
                    position=self.map_point((900, 400)),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="thiago_saguao_welcome",
                    use_player_animations=True,
                    interactable=False,
                ),
                self.create_student_npc(
                    "saguao_student_1",
                    (125, 215),
                    ("O saguão fica bem cheio antes do começo das aulas.",),
                ),
                self.create_student_npc(
                    "saguao_student_2",
                    (220, 215),
                    ("A sala do laboratório fica no fim do corredor.",),
                ),
                NPC(
                    npc_id="saguao_aluna_dracula",
                    display_name="Aluna",
                    position=self.map_point((545, 215)),
                    sprite_path=(
                        "assets/sprites/player/"
                        "TheFemaleAdventurer/Idle/Idle_Up.png"
                    ),
                    dialogue_id="aluna_dracula_saguao",
                    use_player_animations=True,
                    animation_scale=3,
                ),
                self.create_student_npc(
                    "saguao_student_4",
                    (690, 380),
                    ("Estou esperando meus colegas para a próxima aula.",),
                ),
                self.create_student_npc(
                    "saguao_walker_1",
                    (365, 410),
                    ("Com licença, estou procurando minha sala.",),
                ),
                self.create_student_npc(
                    "saguao_walker_2",
                    (680, 500),
                    ("Ainda tenho alguns minutos antes da aula.",),
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
            dialogue_from_id("thiago_saguao_welcome"),
            npc(
                "professor_thiago_saguao",
                self.map_point((900, 130)),
            ),
            fade_out("professor_thiago_saguao", duration=0.25),
            npcs(
                {
                    "saguao_student_1": self.map_point((800, 100)),
                    "saguao_student_2": self.map_point((850, 100)),
                    "saguao_student_4": self.map_point((900, 100)),
                }
            ),
            fade_out("saguao_student_1", duration=0.25),
            fade_out("saguao_student_2", duration=0.25),
            fade_out("saguao_student_4", duration=0.25),
            player_destination(self.map_point((900, 100))),
            change_scene(
                lambda: Laboratorio6(game),
                player_spawn=Laboratorio6.map_point((820, 120)),
            ),
            cutscene_id="first_day_saguao",
            bounds=self.bounds,
            camera=self.camera,
        )
        self.cutscene_controller.start()

    def handle_event(self, event):
        """Delega falas da história e encaminha interações da cena."""
        if self.is_inventory_open():
            return

        if self.cutscene_controller.handle_event(event):
            return

        aluna = self.npc_controller.get_npc("saguao_aluna_dracula")
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and self.game.dialogue_manager.is_active
            and self.npc_controller.pending_interaction_npc is aluna
        ):
            self.npc_controller.handle_event(event)
            if (
                not self.game.dialogue_manager.is_active
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
            for item in self.items:
                if item.can_interact(self.player):
                    item.pick_up(self.player)
                    return

            if self.lab_door.can_interact(self.player):
                self.game.scene_manager.transition_to(
                    lambda: Laboratorio6(self.game),
                    player_spawn=self.map_point((900, 150)),
                )
                return

            if self.cantina_door.can_interact(self.player):
                from scenes.cantina import Cantina

                self.game.scene_manager.transition_to(
                    lambda: Cantina(self.game),
                    player_spawn=self.map_point((480, 400)),
                )
                return

            if self.stairs_door.can_interact(self.player):
                from scenes.laboratorio1 import Laboratorio1

                self.game.scene_manager.transition_to(
                    lambda: Laboratorio1(self.game),
                    player_spawn=Laboratorio1._fit_tileset_point((1000, 875)),
                )
                return

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Atualiza a história, os NPCs, os itens e o jogador."""
        for item in self.items:
            item.update()
        self.update_camera(delta_time, self.cutscene_controller)
        self.cutscene_controller.update(delta_time)
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=(),
        )
        aluna = self.npc_controller.get_npc("saguao_aluna_dracula")
        if (
            self.aluna_thought_pending
            and not self.game.dialogue_manager.is_active
            and self.player.position.distance_to(aluna.position)
            > aluna.interaction_radius + 40
        ):
            self.game.dialogue_manager.start("aluna_vampire_thought")
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
        for item in self.items:
            item.draw(world)
        self.draw_scene_entities(world, self.npc_controller.npcs)
        self.render_world(screen)

        nearby_item = next((item for item in self.items if item.can_interact(self.player)), None)
        if nearby_item is not None:
            prompt = self.hint_font.render(
                f"Pressione E para coletar {nearby_item.name}",
                True,
                (255, 255, 255),
            )
            screen.blit(
                prompt,
                self.game.dialogue_manager.stack_bubble_rect(
                    prompt.get_rect(
                        midbottom=(
                            screen.get_width() // 2,
                            screen.get_height() - 18,
                        )
                    )
                ),
            )

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
