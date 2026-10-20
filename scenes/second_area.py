"""Cena de demonstração conectada à cena principal por uma porta."""

import random

import pygame

from entities.door import Door
from entities.npc import NPC
from config import SCREEN_HEIGHT, SCREEN_WIDTH
from scenes.scene import Scene
from systems.collision import get_entity_hitbox
from systems.navigation import find_path
from systems.npc_controller import NPCController


class SecondArea(Scene):
    """Área com porta, jogador e NPCs que passeiam usando navegação com colisões."""

    NPC_WANDER_INTERVAL = 5.0
    NPC_REPATH_INTERVAL = 0.5
    NAVIGATION_CELL_SIZE = 16

    def __init__(self, game, player_spawn=(145, 300)):
        """Cria a área e inicializa dois NPCs ambulantes."""
        super().__init__(game)
        self.player = game.player
        self.player.position.update(player_spawn)
        self.player.rect.center = player_spawn
        surface = pygame.display.get_surface()
        self.bounds = pygame.Rect(
            0,
            0,
            surface.get_width() if surface else SCREEN_WIDTH,
            surface.get_height() if surface else SCREEN_HEIGHT,
        )
        self.background_color = (48, 66, 58)
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            36,
        )
        self.door = Door(
            rect=(42, 245, 56, 112),
            prompt="Voltar para a área anterior",
        )
        ambient_lines = game.dialogue_manager.dialogues["falas_aleatorias"]
        self.npcs = [
            NPC(
                npc_id="estudante_area_2_a",
                display_name="Estudante",
                position=(320, 190),
                sprite_path="assets/sprites/npcs/Idle_Down.png",
                dialogue_id="poema",
                ambient_radius=220,
                ambient_lines=ambient_lines,
                use_player_animations=True,
                interactable=False,
            ),
            NPC(
                npc_id="estudante_area_2_b",
                display_name="Estudante",
                position=(700, 420),
                sprite_path="assets/sprites/npcs/Idle_Down.png",
                dialogue_id="poema",
                ambient_radius=220,
                ambient_lines=ambient_lines,
                use_player_animations=True,
                interactable=False,
            ),
        ]
        self.npc_controller = NPCController(game, self.npcs)
        self.wanderers = {
            npc: {
                "timer": 0.0,
                "path": [],
                "path_index": 0,
                "target": None,
                "repath_timer": 0.0,
            }
            for npc in self.npcs
        }

    def handle_event(self, event):
        """Inicia o fade para a cena principal ao interagir com a porta."""
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and self.door.can_interact(self.player)
        ):
            from scenes.game_scene import GameScene

            self.game.scene_manager.transition_to(
                lambda: GameScene(self.game, player_spawn=(840, 300))
            )

    def update(self, delta_time):
        """Move entidades com colisão e escolhe destinos dos NPCs a cada cinco segundos."""
        obstacles = [self.door.rect]
        obstacles.extend(
            get_entity_hitbox(npc)
            for npc in self.npcs
        )
        self.player.update(
            delta_time,
            bounds=self.bounds,
            obstacles=obstacles,
        )

        self._update_wanderers(delta_time)
        self.npc_controller.update(delta_time)

    def _update_wanderers(self, delta_time):
        """Planeja e segue rotas livres de colisão para cada NPC ambulante."""
        for npc, state in self.wanderers.items():
            state["timer"] -= delta_time
            if state["timer"] <= 0:
                self._choose_wander_target(npc, state)
                state["timer"] = self.NPC_WANDER_INTERVAL

            state["repath_timer"] = max(
                0.0,
                state["repath_timer"] - delta_time,
            )
            path = state["path"]
            while path and state["path_index"] < len(path):
                obstacles = self._get_npc_obstacles(npc)
                target = path[state["path_index"]]
                previous_position = npc.position.copy()
                arrived = npc.move_towards(
                    target,
                    delta_time,
                    bounds=self.bounds,
                    obstacles=obstacles,
                    keep_walking=(
                        state["path_index"] < len(path) - 1
                    ),
                )

                if npc.position == previous_position:
                    if state["repath_timer"] == 0:
                        state["path"] = find_path(
                            npc,
                            state["target"],
                            self.bounds,
                            obstacles,
                            self.NAVIGATION_CELL_SIZE,
                        )
                        state["path_index"] = 0
                        state["repath_timer"] = self.NPC_REPATH_INTERVAL
                    break

                if not arrived:
                    break
                state["path_index"] += 1

    def _choose_wander_target(self, npc, state):
        """Sorteia um destino navegável dentro da área livre da tela."""
        for _ in range(12):
            target = pygame.Vector2(
                random.randrange(160, self.bounds.right - 32, self.NAVIGATION_CELL_SIZE),
                random.randrange(96, self.bounds.bottom - 32, self.NAVIGATION_CELL_SIZE),
            )
            obstacles = self._get_npc_obstacles(npc)
            path = find_path(
                npc,
                target,
                self.bounds,
                obstacles,
                self.NAVIGATION_CELL_SIZE,
            )
            if path:
                state["target"] = target
                state["path"] = path
                state["path_index"] = 0
                return

        state["target"] = None
        state["path"] = []
        state["path_index"] = 0

    def _get_npc_obstacles(self, moving_npc):
        """Retorna porta, jogador e demais NPCs como obstáculos da rota."""
        obstacles = [
            self.door.rect,
            get_entity_hitbox(self.player),
        ]
        obstacles.extend(
            get_entity_hitbox(npc)
            for npc in self.npcs
            if npc is not moving_npc
        )
        return obstacles

    def draw(self, screen):
        """Desenha o fundo, porta, NPCs, jogador e suas falas compactas."""
        screen.fill(self.background_color)

        title = self.title_font.render(
            "Segunda área",
            True,
            (255, 255, 255),
        )
        screen.blit(title, (24, 20))

        self.door.draw(screen, self.player)
        self.npc_controller.draw_npcs(screen)
        screen.blit(self.player.image, self.player.rect)
        self.npc_controller.draw_ui(screen)
