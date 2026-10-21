from dataclasses import dataclass

from systems.cutscene import Cutscene
from systems.trigger import Trigger as AreaTrigger


@dataclass(frozen=True)
class CutsceneAction:
    """Descreve uma ação declarativa para compor uma cutscene."""

    kind: str
    options: dict


def npc(npc_id, npc_arrival):
    """Cria uma ação de movimento para o NPC identificado por npc_id."""
    return CutsceneAction(
        "npc",
        {"npc_id": npc_id, "destination": npc_arrival},
    )


def player_destination(destination, obstacles=()):
    """Cria uma ação de movimento do jogador até um destino."""
    return CutsceneAction(
        "player",
        {"destination": destination, "obstacles": tuple(obstacles)},
    )


def wait(seconds):
    """Cria uma pausa temporizada na sequência."""
    return CutsceneAction("wait", {"seconds": seconds})


def dialogue(text, speaker="Calouro", face_npc=None):
    """Cria uma fala inline, sem exigir uma entrada no JSON."""
    return CutsceneAction(
        "dialogue",
        {"text": text, "speaker": speaker, "face_npc": face_npc},
    )


def dialogue_from_id(dialogue_id, speaker="", face_npc=None):
    """Cria uma fala consultada pelo identificador no arquivo de diálogos."""
    return CutsceneAction(
        "dialogue_from_id",
        {
            "dialogue_id": dialogue_id,
            "speaker": speaker,
            "face_npc": face_npc,
        },
    )


def npc_dialogue(npc_id, text, face_player=True):
    """Cria uma fala inline atribuída ao NPC indicado."""
    return CutsceneAction(
        "npc_dialogue",
        {"npc_id": npc_id, "text": text, "face_player": face_player},
    )


def trigger(
    trigger_position=None,
    trigger_radius=None,
    action=None,
    visible=False,
    trigger_rect=None,
):
    """Cria um gatilho de entrada e as ações a executar quando ativado."""
    # O gatilho deve definir exatamente uma geometria: círculo ou retângulo.
    if trigger_rect is None and (
        trigger_position is None or trigger_radius is None
    ):
        raise ValueError("Informe trigger_rect ou posição e raio.")
    if trigger_rect is not None and (
        trigger_position is not None or trigger_radius is not None
    ):
        raise ValueError("Use trigger_rect ou posição e raio, não ambos.")
    if action is None:
        raise ValueError("Informe ao menos uma ação para o trigger.")

    if isinstance(action, CutsceneAction):
        actions = (action,)
    else:
        actions = tuple(action)
    # Exige ações presentes; em seguida valida o tipo de cada uma.
    if not actions or not all(
        isinstance(item, CutsceneAction) for item in actions
    ):
        raise TypeError("As ações do trigger devem ser CutsceneAction.")
    return CutsceneAction(
        "trigger",
        {
            "position": trigger_position,
            "radius": trigger_radius,
            "rect": trigger_rect,
            "visible": visible,
            "actions": actions,
        },
    )


class CutsceneController:
    """Executa sequências de gatilhos, movimento, orientação e diálogo."""

    def __init__(
        self,
        player,
        npc_controller,
        dialogue_manager,
        bounds=None,
    ):
        self.player = player
        self.npc_controller = npc_controller
        self.dialogue_manager = dialogue_manager
        self.bounds = bounds
        self.steps = []
        self.step_index = 0
        self.is_active = False
        self.waiting_for = None
        self.waiting_for_npc_ids = ()
        self.player_obstacles = ()
        self.player_cutscene = Cutscene()
        self.trigger = None
        self.triggers = []
        self.wait_timer = 0.0

    @classmethod
    def create_story_cutscene(
        cls,
        game,
        npc_controller,
        *actions,
        bounds=None,
    ):
        """Monta uma sequência a partir de ações declarativas."""
        cutscene = cls(
            game.player,
            npc_controller,
            game.dialogue_manager,
            bounds=bounds,
        )
        if not actions:
            raise ValueError("Informe ao menos uma ação para a cutscene.")
        for action in actions:
            cutscene.add_action(action)
        return cutscene

    @property
    def is_player_moving(self):
        return self.waiting_for == "player_movement"

    @property
    def locks_player_control(self):
        # O jogador pode andar livremente enquanto aguarda entrar no gatilho.
        return self.is_active and self.waiting_for != "trigger"

    def wait_for_trigger(self, trigger):
        """Adiciona uma etapa que aguarda o jogador entrar em um gatilho."""
        self.steps.append(("trigger", trigger))
        return self

    def add_action(self, action):
        """Converte uma ação declarativa em etapas executáveis."""
        if not isinstance(action, CutsceneAction):
            raise TypeError("Cada etapa deve ser criada por um helper da cutscene.")

        options = action.options
        if action.kind == "npc":
            self.move_npc(options["npc_id"], [options["destination"]])
        elif action.kind == "player":
            self.move_player(
                [options["destination"]],
                obstacles=options["obstacles"],
            )
        elif action.kind == "wait":
            seconds = options["seconds"]
            if seconds < 0:
                raise ValueError("A duração de wait não pode ser negativa.")
            self.steps.append(("wait", seconds))
        elif action.kind == "dialogue":
            self.steps.append(
                (
                    "inline_dialogue",
                    (
                        (options["text"],),
                        options["speaker"],
                        options["face_npc"],
                    ),
                )
            )
        elif action.kind == "dialogue_from_id":
            self.steps.append(
                (
                    "dialogue",
                    (
                        options["dialogue_id"],
                        options["speaker"],
                        options["face_npc"],
                    ),
                )
            )
        elif action.kind == "npc_dialogue":
            self.steps.append(
                (
                    "npc_dialogue",
                    (
                        options["npc_id"],
                        options["text"],
                        options["face_player"],
                    ),
                )
            )
        elif action.kind == "trigger":
            # Cada trigger entra na sequência e executa suas ações logo depois.
            if options["rect"] is not None:
                area_trigger = AreaTrigger(
                    rect=options["rect"],
                    once=True,
                )
            else:
                area_trigger = AreaTrigger(
                    position=options["position"],
                    radius=options["radius"],
                    once=True,
                )
            self.steps.append(("trigger", area_trigger))
            self.triggers.append((area_trigger, options["visible"]))
            for nested_action in options["actions"]:
                self.add_action(nested_action)
        else:
            raise ValueError(f"Ação de cutscene desconhecida: {action.kind}")
        return self

    def move_npc(self, npc_id, points):
        """Adiciona uma etapa que move um NPC registrado por pontos."""
        return self.move_npcs({npc_id: points})

    def move_npcs(self, movements):
        """Move vários NPCs em paralelo, cada um seguindo seus próprios pontos."""
        if not movements:
            raise ValueError("Informe ao menos um NPC para movimentar.")

        self.steps.append(
            (
                "npc_movements",
                tuple(
                    (npc_id, tuple(points))
                    for npc_id, points in movements.items()
                ),
            )
        )
        return self

    def move_player(self, points, obstacles=()):
        """Adiciona uma etapa que move o jogador por pontos do cenário."""
        self.steps.append(("player_movement", (tuple(points), tuple(obstacles))))
        return self

    def face_npc(self, npc_id, target="player"):
        """Adiciona uma etapa que orienta o NPC para o jogador ou uma posição."""
        self.steps.append(("face_npc", (npc_id, target)))
        return self

    def dialogue(self, dialogue_id, speaker="", face_npc=None):
        """Adiciona uma fala e, opcionalmente, orienta um NPC para o jogador."""
        self.steps.append(("dialogue", (dialogue_id, speaker, face_npc)))
        return self

    def draw_trigger(self, screen):
        """Desenha o gatilho do roteiro, se este possuir um."""
        for area_trigger, visible in self.triggers:
            # Só desenha gatilhos marcados como visíveis e ainda não acionados.
            if visible and not area_trigger.has_triggered:
                area_trigger.draw(screen)

    def start(self):
        """Inicia a sequência a partir da primeira etapa configurada."""
        if self.is_active:
            return False
        if not self.steps:
            raise ValueError("A cutscene precisa de pelo menos uma etapa.")

        self.step_index = 0
        self.waiting_for = None
        self.waiting_for_npc_ids = ()
        self.is_active = True
        self._run_ready_steps()
        return True

    def handle_event(self, event):
        """Encaminha eventos ao diálogo somente enquanto a cutscene fala."""
        # Fora de uma fala, evita teclas como E vazarem para interações da cena.
        if self.waiting_for != "dialogue":
            return self.locks_player_control

        self.dialogue_manager.handle_event(event)
        return True

    def update(self, delta_time):
        """Avança a etapa ativa e executa etapas prontas em sequência."""
        if not self.is_active:
            return

        if self.waiting_for == "player_movement":
            self.player_cutscene.update(
                delta_time,
                bounds=self.bounds,
                obstacles=self.npc_controller.get_player_obstacles(
                    self.player_obstacles
                ),
            )
            if self.player_cutscene.is_active:
                return
            self._finish_current_step()

        elif self.waiting_for == "npc_movement":
            if any(
                self.npc_controller.is_npc_moving(npc_id)
                for npc_id in self.waiting_for_npc_ids
            ):
                return
            self.waiting_for_npc_ids = ()
            self._finish_current_step()

        elif self.waiting_for == "trigger":
            trigger = self.steps[self.step_index][1]
            if not trigger.update(self.player):
                return
            self._finish_current_step()

        elif self.waiting_for == "dialogue":
            if self.dialogue_manager.is_active:
                return
            self._finish_current_step()

        elif self.waiting_for == "wait":
            self.wait_timer -= delta_time
            if self.wait_timer > 0:
                return
            self._finish_current_step()

        self._run_ready_steps()

    def _run_ready_steps(self):
        # Executa etapas imediatas até encontrar uma ação que precise aguardar.
        # Continua apenas com cutscene ativa e sem etapa aguardando evento/tempo.
        while self.is_active and self.waiting_for is None:
            if self.step_index >= len(self.steps):
                self.is_active = False
                return

            action, arguments = self.steps[self.step_index]
            if action == "trigger":
                self.waiting_for = "trigger"
                return

            elif action == "wait":
                self.wait_timer = arguments
                if self.wait_timer > 0:
                    self.waiting_for = "wait"
                    return
                self._finish_current_step()
                continue

            elif action == "npc_movements":
                active_npc_ids = []
                for npc_id, points in arguments:
                    npc = self.npc_controller.get_npc(npc_id)
                    cutscene = self.npc_controller.start_npc_cutscene(
                        npc,
                        points,
                    )
                    if cutscene.is_active:
                        active_npc_ids.append(npc_id)
                if active_npc_ids:
                    self.waiting_for_npc_ids = tuple(active_npc_ids)
                    self.waiting_for = "npc_movement"
                    return

            elif action == "player_movement":
                points, obstacles = arguments
                if not points:
                    raise ValueError(
                        "O movimento da cutscene precisa de destinos."
                    )
                self.player_obstacles = obstacles
                self.player_cutscene.start(self.player, points)
                if self.player_cutscene.is_active:
                    self.waiting_for = "player_movement"
                    return

            elif action == "face_npc":
                npc_id, target = arguments
                if target == "player":
                    target = self.player
                self.npc_controller.face_npc(npc_id, target)

            elif action == "dialogue":
                dialogue_id, speaker, face_npc = arguments
                if self.dialogue_manager.is_active:
                    return
                if face_npc is not None:
                    npc = self.npc_controller.get_npc(face_npc)
                    self.npc_controller.face_npc(face_npc, self.player)
                    self.player.look_at(npc.position)
                if self.dialogue_manager.start(
                    dialogue_id,
                    speaker=speaker,
                ):
                    self.waiting_for = "dialogue"
                    return

            elif action == "inline_dialogue":
                lines, speaker, face_npc = arguments
                if self.dialogue_manager.is_active:
                    return
                if face_npc is not None:
                    npc = self.npc_controller.get_npc(face_npc)
                    self.npc_controller.face_npc(face_npc, self.player)
                    self.player.look_at(npc.position)
                if self.dialogue_manager.start_lines(lines, speaker=speaker):
                    self.waiting_for = "dialogue"
                    return

            elif action == "npc_dialogue":
                npc_id, text, face_player = arguments
                if self.dialogue_manager.is_active:
                    return
                npc = self.npc_controller.get_npc(npc_id)
                if face_player:
                    self.npc_controller.face_npc(npc_id, self.player)
                    self.player.look_at(npc.position)
                if self.dialogue_manager.start_lines(
                    (text,),
                    speaker=npc.display_name,
                ):
                    self.waiting_for = "dialogue"
                    return

            else:
                raise ValueError(f"Ação de cutscene desconhecida: {action}")

            self._finish_current_step()

    def _finish_current_step(self):
        self.step_index += 1
        self.waiting_for = None
