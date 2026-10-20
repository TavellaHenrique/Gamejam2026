
import random

import pygame

from systems.cutscene import Cutscene
from ui.dialogue_box import DialogueBox


class NPCController:
    """Coordena NPCs, interações do jogador e a interface de diálogo."""

    AMBIENT_SPEECH_CHANCE = 30
    AMBIENT_SPEECH_COOLDOWN = 8.0
    AMBIENT_SPEECH_DURATION = 3.0
    SIDE_APPROACH_DISTANCE = 80
    SIDE_APPROACH_Y_OFFSET = 0
    BELOW_APPROACH_DISTANCE = 80
    BELOW_Y_THRESHOLD = 40
    BELOW_X_THRESHOLD = 42

    def __init__(self, game, npcs=()):
        """Guarda referências do jogo e prepara os NPCs e elementos da interface."""
        # Reutiliza os objetos centrais do jogo para consultar o jogador e controlar diálogos.
        self.player = game.player
        self.dialogue_manager = game.dialogue_manager

        # O grupo permite atualizar e desenhar todos os NPCs usando as APIs do Pygame.
        self.npcs = pygame.sprite.Group(*npcs)

        # A caixa exibe as falas; active_speaker guarda o nome mostrado durante o diálogo.
        self.dialogue_box = DialogueBox()
        self.active_speaker = ""

        # Controla entradas na área de fala e evita falas aleatórias em sequência.
        self.nearby_ambient_npcs = set()
        self.ambient_speech_cooldown = 0.0
        self.ambient_speech_timer = 0.0
        self.ambient_speaker = ""
        self.ambient_npc = None
        self.interaction_cutscene = Cutscene()
        self.pending_interaction_npc = None
        self.previous_npc_facing = None
        self.is_approaching_npc = False

        # Fonte usada no aviso de interação que aparece perto do NPC mais próximo.
        self.prompt_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf", 20
        )

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
        """Processa a tecla de interação para iniciar ou avançar um diálogo."""
        # Outros eventos e teclas não afetam o controlador de NPCs.
        if event.type != pygame.KEYDOWN:
            return

        if event.key != pygame.K_e:
            return

        # Durante um diálogo, E primeiro tenta avançar a página visível.
        if self.dialogue_manager.is_active:
            if self.dialogue_box.advance_page():
                return

            # Quando não há outra página, solicita ao gerenciador a próxima fala.
            self.dialogue_manager.advance()

            # Atualiza a caixa caso ainda haja diálogo ou limpa o personagem ao terminar.
            if self.dialogue_manager.is_active:
                self.dialogue_box.show_text(
                    self.dialogue_manager.current_text
                )
            else:
                self.active_speaker = ""
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
            offset.y >= self.BELOW_Y_THRESHOLD
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
            self.pending_interaction_npc.facing = self.previous_npc_facing
            self.pending_interaction_npc._select_animation(moving=False)
            self.pending_interaction_npc._apply_facing_image()

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
        self.active_speaker = npc.display_name
        self.dialogue_manager.start(npc.dialogue_id)
        self.dialogue_box.show_text(self.dialogue_manager.current_text)
        self.is_approaching_npc = False

    def _clear_ambient_speech(self):
        """Esconde a fala aleatória e libera a referência ao NPC que a disse."""
        self.ambient_speech_timer = 0.0
        self.ambient_npc = None

    def update(self, delta_time):
        """Atualiza NPCs e verifica entradas na área de falas aleatórias."""
        self.interaction_cutscene.update(delta_time)

        if self.pending_interaction_npc is not None:
            npc = self.pending_interaction_npc
            npc.look_at(self.player.position)

            if (
                self.is_approaching_npc
                and not self.interaction_cutscene.is_active
            ):
                self._begin_pending_dialogue()

        self.npcs.update(delta_time)
        self.ambient_speech_cooldown = max(
            0.0,
            self.ambient_speech_cooldown - delta_time,
        )
        if self.ambient_speech_timer > 0:
            self.ambient_speech_timer = max(
                0.0,
                self.ambient_speech_timer - delta_time,
            )
            if self.ambient_speech_timer == 0:
                self._clear_ambient_speech()

        # Mantém os NPCs com falas aleatórias dentro da área de proximidade.
        currently_nearby = {
            npc for npc in self.npcs
            if npc.ambient_lines and npc.is_in_ambient_range(self.player)
        }
        self.nearby_ambient_npcs = currently_nearby

        # Tenta novamente após cada cooldown, mesmo que o jogador não saia da área.
        if (
            not currently_nearby
            or self.ambient_speech_cooldown > 0
            or self.dialogue_manager.is_active
            or self.pending_interaction_npc is not None
        ):
            return

        # O cooldown começa após qualquer tentativa, mesmo quando a chance falha.
        self.ambient_speech_cooldown = self.AMBIENT_SPEECH_COOLDOWN
        if random.randint(1, 100) > self.AMBIENT_SPEECH_CHANCE:
            return

        # Sorteia um NPC próximo e uma fala configurada para ele.
        npc = random.choice(tuple(currently_nearby))
        line = random.choice(npc.ambient_lines)
        self.ambient_speaker = npc.display_name
        self.ambient_npc = npc
        self.ambient_text = line
        self.ambient_speech_timer = self.AMBIENT_SPEECH_DURATION

    def draw_npcs(self, screen):
        """Desenha todos os sprites de NPC na superfície da tela."""
        self.npcs.draw(screen)

    def draw_ui(self, screen):
        """Desenha o diálogo ativo ou o aviso para interagir com um NPC próximo."""
        # O diálogo tem prioridade sobre o aviso; ao desenhá-lo, encerra esta etapa.
        if self.dialogue_manager.is_active:
            self.dialogue_box.draw(
                screen,
                speaker_name=self.active_speaker,
            )
            return

        if self.pending_interaction_npc is not None:
            return

        # Falas aleatórias desaparecem sozinhas e não bloqueiam o movimento.
        if self.ambient_speech_timer > 0:
            self._draw_compact_bubble(
                screen,
                self.ambient_npc,
                f"{self.ambient_speaker}: {self.ambient_text}",
            )
            return

        # Sem diálogo ativo, procura um NPC para o qual o jogador possa interagir.
        npc = self.get_nearest_interactable_npc()

        if npc is None:
            return

        self._draw_compact_bubble(screen, npc, "E - Interagir")

    def _draw_compact_bubble(self, screen, npc, text):
        """Desenha um balão compacto ancorado acima do NPC."""
        max_width = screen.get_width() - 40
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            candidate = f"{current_line} {word}".strip()
            if current_line and self.prompt_font.size(candidate)[0] > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate

        if current_line:
            lines.append(current_line)

        rendered_lines = [
            self.prompt_font.render(line, True, (255, 255, 255))
            for line in lines
        ]
        text_width = max(line.get_width() for line in rendered_lines)
        line_height = self.prompt_font.get_linesize()
        padding_x = 8
        padding_y = 5
        bubble_width = text_width + padding_x * 2
        bubble_height = len(rendered_lines) * line_height + padding_y * 2
        image_left = round(npc.position.x - npc.image.get_width() / 2)
        image_top = round(npc.position.y - npc.image.get_height() / 2)
        visible_bounds = npc.image.get_bounding_rect()
        npc_x = image_left + visible_bounds.centerx
        npc_top = image_top + visible_bounds.top
        bubble_x = max(
            8,
            min(
                npc_x - bubble_width // 2,
                screen.get_width() - bubble_width - 8,
            ),
        )
        bubble_y = max(8, npc_top - bubble_height - 4)
        background_rect = pygame.Rect(
            bubble_x,
            bubble_y,
            bubble_width,
            bubble_height,
        )
        background = pygame.Surface(
            background_rect.size,
            pygame.SRCALPHA,
        )
        background.fill((20, 24, 32, 210))
        screen.blit(background, background_rect.topleft)

        for index, line in enumerate(rendered_lines):
            screen.blit(
                line,
                (
                    bubble_x + padding_x,
                    bubble_y + padding_y + index * line_height,
                ),
            )
