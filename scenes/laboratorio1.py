import pygame

from entities.door import Door
from entities.npc import NPC
from scenes.saguao import Saguao
from systems.npc_controller import NPCController
from systems.tilemap_scene import LABORATORY_OBSTACLES, TilemapScene


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
                    position=self._fit_tileset_point((1800, 700)),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="adriano_lab1_1",
                    use_player_animations=True,
                    animation_scale=3,
                    interactable=True,
                ),
                self.create_student_npc(
                    "lab1_student_1",
                    (700, 550),
                    ("Estou revisando o conteúdo antes da próxima aula.",),
                ),
                self.create_student_npc(
                    "lab1_student_2",
                    (390, 430),
                    ("Os computadores do laboratório ajudam bastante.",),
                ),
                self.create_student_npc(
                    "lab1_student_3",
                    (550, 315),
                    ("Você já terminou o exercício?",),
                ),
                self.create_student_npc(
                    "lab1_student_4",
                    (700, 390),
                    ("Vou salvar meu trabalho antes de sair.",),
                ),
                self.create_student_npc(
                    "lab1_walker_1",
                    (390, 545),
                    ("Acho que deixei meu caderno em outra mesa.",),
                ),
                self.create_student_npc(
                    "lab1_walker_2",
                    (760, 535),
                    ("Ainda dá tempo de tirar uma dúvida com o professor.",),
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
        self.npc_controller.handle_event(event)

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
