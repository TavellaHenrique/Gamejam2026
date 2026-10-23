"""Cena de exploração do laboratório da professora."""

import pygame

from entities.door import Door
from scenes.saguao import Saguao
from scenes.laboratorio_professora.layout import (
    create_environment_obstacles,
    create_laboratory_objects,
)
from systems.tilemap_scene import TilemapScene


class LaboratorioProfessora(TilemapScene):
    """Laboratório sem NPCs, pronto para receber conteúdo posteriormente."""

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

    def handle_event(self, event):
        """Volta ao saguão quando o jogador interage com a porta de saída."""
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

    def update(self, delta_time):
        """Atualiza câmera e jogador respeitando as colisões do laboratório."""
        self.update_camera(delta_time, None)
        self.player.update(
            delta_time,
            accept_input=(
                not self.game.inventory_open
                and not self.game.dialogue_manager.is_active
            ),
            bounds=self.bounds,
            obstacles=self.get_scene_obstacles(),
        )

    def draw(self, screen):
        """Renderiza o cenário, os objetos ordenados e a interface da cena."""
        world = self.begin_world_draw()
        self.draw_scene_entities(world, ())
        self.render_world(screen)

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
