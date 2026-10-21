
import random

import pygame

from systems.collision import get_entity_hitbox
from systems.cutscene import Cutscene
from systems.navigation import find_path


class NPCController:
    """Coordena NPCs, interações do jogador e a interface de diálogo."""

    NPC_WANDER_INTERVAL = 5.0
    NPC_REPATH_INTERVAL = 0.5
    NAVIGATION_CELL_SIZE = 16
    SIDE_APPROACH_DISTANCE = 80
    SIDE_APPROACH_Y_OFFSET = 0
    BELOW_APPROACH_DISTANCE = 80
    BELOW_Y_THRESHOLD = 40
    BELOW_X_THRESHOLD = 42

    def __init__(self, game, npcs=(), npc_scope=None):
        """Guarda referências do jogo e prepara os NPCs e elementos da interface."""
        self.game = game
        self.npc_scope = npc_scope
        # Reutiliza os objetos centrais do jogo para consultar o jogador e controlar diálogos.
        self.player = game.player
        self.dialogue_manager = game.dialogue_manager

        # O grupo permite atualizar e desenhar todos os NPCs usando as APIs do Pygame.
        available_npcs = (
            npc for npc in npcs
            if not game.is_npc_removed(npc.npc_id, self.npc_scope)
        )
        self.npcs = pygame.sprite.Group(*available_npcs)
        npc_ids = [npc.npc_id for npc in self.npcs]
        if len(npc_ids) != len(set(npc_ids)):
            raise ValueError("Cada NPC precisa ter um npc_id único.")

        # Controla entradas dos NPCs na área de fala ambiente.
        self.nearby_ambient_npcs = set()
        self.interaction_cutscene = Cutscene()
        self.npc_cutscenes = {}
        self.pending_interaction_npc = None
        self.previous_npc_facing = None
        self.is_approaching_npc = False
        self.wander_bounds = None
        self.wander_obstacles = ()
        self.wanderers = {}

    @property
    def is_npc_cutscene_active(self):
        """Indica se um NPC está seguindo um trajeto roteirizado."""
        return any(
            cutscene.is_active
            for cutscene in self.npc_cutscenes.values()
        )

    def configure_wandering(self, npcs, bounds, obstacles=()):
        """Configura NPCs para passear dentro dos limites da área."""
        self.wander_bounds = pygame.Rect(bounds)
        self.wander_obstacles = tuple(obstacles)
        self.wanderers = {
            npc: {
                "timer": 0.0,
                "path": [],
                "path_index": 0,
                "target": None,
                "repath_timer": 0.0,
            }
            for npc in npcs
        }

    def start_npc_cutscene(self, npc, points):
        """Move um NPC registrado por uma sequência de pontos."""
        if isinstance(npc, str):
            npc = self.get_npc(npc)
        if npc not in self.npcs:
            raise ValueError("O NPC da cutscene não está registrado.")

        cutscene = Cutscene()
        cutscene.start(npc, points)
        self.npc_cutscenes[npc] = cutscene
        return cutscene

    def add_npc(self, npc):
        """Adiciona um NPC à cena ativa, validando o identificador."""
        if any(existing.npc_id == npc.npc_id for existing in self.npcs):
            raise ValueError(f"NPC já registrado: {npc.npc_id}")
        self.npcs.add(npc)
        return npc

    def remove_npc(self, npc_id):
        """Remove um NPC e limpa referências de movimento/interação."""
        npc = self.get_npc(npc_id)
        self.npcs.remove(npc)
        self.game.mark_npc_removed(npc_id, self.npc_scope)
        self.npc_cutscenes.pop(npc, None)
        self.wanderers.pop(npc, None)
        self.nearby_ambient_npcs.discard(npc)
        if self.pending_interaction_npc is npc:
            self.pending_interaction_npc = None
            self.previous_npc_facing = None
            self.is_approaching_npc = False
            self.interaction_cutscene.is_active = False
        if self.dialogue_manager.ambient_anchor is npc:
            self.dialogue_manager.clear_ambient_speech()
        return npc

    def get_npc(self, npc_id):
        """Retorna um NPC registrado pelo identificador."""
        for npc in self.npcs:
            if npc.npc_id == npc_id:
                return npc

        raise KeyError(f"NPC não encontrado: {npc_id}")

    def has_npc(self, npc_id):
        """Indica se existe um NPC registrado com o identificador informado."""
        return any(npc.npc_id == npc_id for npc in self.npcs)

    def face_direction(self, npc_id, direction):
        """Orienta um NPC para um vetor ou direção cardinal/diagonal."""
        directions = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
            "up_left": (-1, -1),
            "up_right": (1, -1),
            "down_left": (-1, 1),
            "down_right": (1, 1),
        }
        vector = (
            directions[direction]
            if isinstance(direction, str)
            else direction
        )
        self.get_npc(npc_id).set_facing(vector)

    def is_npc_moving(self, npc_id):
        """Indica se o NPC está executando um trajeto roteirizado."""
        npc = self.get_npc(npc_id)
        cutscene = self.npc_cutscenes.get(npc)
        # Confirma primeiro a existência do trajeto e depois que ele segue ativo.
        return cutscene is not None and cutscene.is_active

    def get_player_obstacles(self, static_obstacles=()):
        """Retorna obstáculos estáticos e hitboxes dos NPCs para o jogador."""
        return [
            *static_obstacles,
            *(
                get_entity_hitbox(npc)
                for npc in self.npcs
            ),
        ]

    def get_nearest_interactable_npc(self):
        """Retorna o NPC interagível mais próximo ou None se não houver algum."""
        # Primeiro, descarta NPCs que não estão em alcance ou não podem ser abordados.
        nearby_npcs = [
            npc for npc in self.npcs
            if npc.can_interact(self.player)
        ]

        # Sem candidatos, não existe interação disponível no momento.
        if not nearby_npcs:
            return None

        # Entre os candidatos, escolhe aquele com menor distância até o jogador.
        return min(
            nearby_npcs,
            key=lambda npc: npc.position.distance_to(
                self.player.position
            ),
        )

    def handle_event(self, event):
        """Encaminha diálogos e interações ao controlador responsável."""
        # Outros eventos e teclas não afetam o controlador de NPCs.
        if event.type != pygame.KEYDOWN:
            return

        if event.key != pygame.K_e:
            return

        if self.dialogue_manager.is_active:
            if self.dialogue_manager.handle_event(event):
                self._restore_npc_facing()
            return

        if self.pending_interaction_npc is not None:
            return

        # Fora de um diálogo, E inicia uma conversa com o NPC elegível mais próximo.
        self.interact_with_nearest_npc()

    def interact_with_nearest_npc(self):
        """Inicia o diálogo do NPC interagível mais próximo do jogador."""
        npc = self.get_nearest_interactable_npc()

        # Não faz nada se não houver NPC disponível para interação.
        if npc is None:
            return

        # Salva a orientação original para restaurá-la quando a conversa terminar.
        self.pending_interaction_npc = npc
        self.previous_npc_facing = npc.facing.copy()
        self._clear_ambient_speech()

        # Prepara uma posição lateral ou abaixo do NPC antes de começar a conversa.
        target = self._get_conversation_position(npc)
        self.interaction_cutscene.start(
            self.player,
            [self.player.position, target],
        )
        npc.look_at(self.player.position)
        self.is_approaching_npc = self.interaction_cutscene.is_active
        if not self.is_approaching_npc:
            self._begin_pending_dialogue()

    def _get_conversation_position(self, npc):
        """Calcula um ponto próximo ao NPC, de frente e sem sobrepor o sprite."""
        offset = self.player.position - npc.position

        if (
            # A aproximação inferior só é adequada quando o jogador está abaixo.
            offset.y >= self.BELOW_Y_THRESHOLD
            # E suficientemente alinhado horizontalmente ao NPC.
            and abs(offset.x) <= self.BELOW_X_THRESHOLD
        ):
            return npc.position + pygame.Vector2(
                0,
                self.BELOW_APPROACH_DISTANCE,
            )

        side = -1 if offset.x < 0 else 1
        y_offset = (
            -self.SIDE_APPROACH_Y_OFFSET
            if offset.y < 0
            else self.SIDE_APPROACH_Y_OFFSET
        )
        return npc.position + pygame.Vector2(
            side * self.SIDE_APPROACH_DISTANCE,
            y_offset,
        )

    def _restore_npc_facing(self):
        """Restaura a direção do NPC salva antes de iniciar a interação."""
        if self.pending_interaction_npc is not None:
            self.pending_interaction_npc.set_facing(
                self.previous_npc_facing
            )

        self.pending_interaction_npc = None
        self.previous_npc_facing = None
        self.is_approaching_npc = False

    def _begin_pending_dialogue(self):
        """Inicia a conversa depois que o jogador conclui a aproximação."""
        npc = self.pending_interaction_npc
        if npc is None:
            return

        npc.look_at(self.player.position)
        self.player.look_at(npc.position)
        self.dialogue_manager.start(
            npc.dialogue_id,
            speaker=npc.display_name,
        )
        self.is_approaching_npc = False

    def _clear_ambient_speech(self):
        """Esconde a fala aleatória e libera a referência ao NPC que a disse."""
        self.dialogue_manager.clear_ambient_speech()

    def update(self, delta_time):
        """Atualiza NPCs e encaminha oportunidades de fala ao DialogueManager."""
        self.dialogue_manager.update(delta_time)
        self.interaction_cutscene.update(delta_time)
        for npc, cutscene in tuple(self.npc_cutscenes.items()):
            cutscene.update(
                delta_time,
                bounds=self.wander_bounds,
                obstacles=self._get_npc_obstacles(npc),
            )
            if not cutscene.is_active:
                del self.npc_cutscenes[npc]
        self._update_wanderers(delta_time)

        if self.pending_interaction_npc is not None:
            npc = self.pending_interaction_npc
            npc.look_at(self.player.position)

            if (
                # A aproximação precisa ter terminado antes de iniciar o diálogo.
                self.is_approaching_npc
                # A cutscene ainda ativa indica que o jogador está em movimento.
                and not self.interaction_cutscene.is_active
            ):
                self._begin_pending_dialogue()

        self.npcs.update(delta_time)

        # Mantém os NPCs com falas aleatórias dentro da área de proximidade.
        # Considera somente NPCs com falas configuradas e dentro do raio.
        currently_nearby = {
            npc for npc in self.npcs
            if npc.ambient_lines and npc.is_in_ambient_range(self.player)
        }
        self.nearby_ambient_npcs = currently_nearby

        if (
            # Sem NPCs próximos ou com diálogo visível, não inicie fala ambiente.
            not currently_nearby
            # Falas normais e balões existentes ocupam o canal de diálogo.
            or self.dialogue_manager.is_active
            # Evita sobrepor dois balões de fala ambiente.
            or self.dialogue_manager.is_ambient_active
            # Uma interação em andamento também tem prioridade.
            or self.pending_interaction_npc is not None
        ):
            return

        self.dialogue_manager.try_start_ambient(currently_nearby)

    def _update_wanderers(self, delta_time):
        """Planeja e segue rotas para os NPCs configurados como errantes."""
        if self.wander_bounds is None:
            return

        for npc, state in self.wanderers.items():
            if npc in self.npc_cutscenes:
                continue

            state["timer"] -= delta_time
            if state["timer"] <= 0:
                self._choose_wander_target(npc, state)
                state["timer"] = self.NPC_WANDER_INTERVAL

            state["repath_timer"] = max(
                0.0,
                state["repath_timer"] - delta_time,
            )
            path = state["path"]
            # Continua apenas com rota e pontos ainda não visitados.
            while path and state["path_index"] < len(path):
                obstacles = self._get_npc_obstacles(npc)
                target = path[state["path_index"]]
                previous_position = npc.position.copy()
                arrived = npc.move_towards(
                    target,
                    delta_time,
                    bounds=self.wander_bounds,
                    obstacles=obstacles,
                    keep_walking=(
                        state["path_index"] < len(path) - 1
                    ),
                )

                # Se não houve avanço, o trajeto está bloqueado e precisa recalcular.
                if npc.position == previous_position:
                    if state["repath_timer"] == 0:
                        state["path"] = find_path(
                            npc,
                            state["target"],
                            self.wander_bounds,
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
        """Sorteia um destino navegável dentro dos limites configurados."""
        for _ in range(12):
            target = pygame.Vector2(
                random.randrange(
                    160,
                    self.wander_bounds.right - 32,
                    self.NAVIGATION_CELL_SIZE,
                ),
                random.randrange(
                    96,
                    self.wander_bounds.bottom - 32,
                    self.NAVIGATION_CELL_SIZE,
                ),
            )
            obstacles = self._get_npc_obstacles(npc)
            path = find_path(
                npc,
                target,
                self.wander_bounds,
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
        """Retorna obstáculos fixos, jogador e demais NPCs para a navegação."""
        obstacles = list(self.wander_obstacles)
        obstacles.append(get_entity_hitbox(self.player))
        obstacles.extend(
            get_entity_hitbox(npc)
            for npc in self.npcs
            if npc is not moving_npc
        )
        return obstacles

    def draw_npcs(self, screen):
        """Desenha todos os sprites de NPC na superfície da tela."""
        self.npcs.draw(screen)

    def draw_ui(self, screen):
        """Desenha os diálogos e os avisos de interação."""
        self.dialogue_manager.draw(screen)

        if (
            # Uma conversa normal ou um balão ambiental já usa essa interface.
            self.dialogue_manager.is_active
            # Não exiba também a dica de interação nesse caso.
            or self.dialogue_manager.is_ambient_active
        ):
            return

        if self.pending_interaction_npc is not None:
            return

        # Sem diálogo ativo, procura um NPC para o qual o jogador possa interagir.
        npc = self.get_nearest_interactable_npc()

        if npc is None:
            return

        self.dialogue_manager.draw_bubble(
            screen,
            npc,
            "E - Interagir",
        )
