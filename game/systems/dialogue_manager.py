import json
import random

import pygame

from game.ui.dialogue_box import DialogueBox


class DialogueManager:
    """Controls dialogue state, progression, ambient speech, and presentation."""

    AMBIENT_SPEECH_CHANCE = 30
    AMBIENT_SPEECH_COOLDOWN = 8.0
    AMBIENT_SPEECH_DURATION = 3.0

    def __init__(self, dialogues_path):
        """Loads dialogue data and initializes the dialogue presentation."""
        with open(dialogues_path, "r", encoding="utf-8") as file:
            self.dialogues = json.load(file)
        for dialogue_id, dialogue in self.dialogues.items():
            if not isinstance(dialogue, dict):
                raise ValueError(
                    f"O diálogo '{dialogue_id}' precisa conter speaker e lines."
                )
            if "speaker" not in dialogue or "lines" not in dialogue:
                raise ValueError(
                    f"O diálogo '{dialogue_id}' precisa conter speaker e lines."
                )

            speaker_indices = {
                key[len("speaker"):]
                for key in dialogue
                if key.startswith("speaker")
                and key[len("speaker"):].isdigit()
            }
            lines_indices = {
                key[len("lines"):]
                for key in dialogue
                if key.startswith("lines")
                and key[len("lines"):].isdigit()
            }
            turn_indices = speaker_indices | lines_indices
            if (
                speaker_indices != lines_indices
                or turn_indices != {
                    str(index)
                    for index in range(
                        2,
                        max(
                            (int(index) for index in turn_indices),
                            default=1,
                        ) + 1,
                    )
                }
            ):
                raise ValueError(
                    f"Os falantes e as falas do diálogo '{dialogue_id}' "
                    "precisam formar pares numerados a partir de 2."
                )

            for index in ("", *sorted(turn_indices, key=int)):
                speaker_key = f"speaker{index}"
                lines_key = f"lines{index}"
                if not isinstance(dialogue[speaker_key], str):
                    raise ValueError(
                        f"O falante '{speaker_key}' do diálogo "
                        f"'{dialogue_id}' precisa ser texto."
                    )
                if not isinstance(dialogue[lines_key], list):
                    raise ValueError(
                        f"As falas '{lines_key}' do diálogo "
                        f"'{dialogue_id}' precisam ser uma lista."
                    )

        self.dialogue_box = DialogueBox()
        self.active_dialogue = None
        self.active_speakers = ()
        self.active_speaker = ""
        self.current_line = 0
        self.current_pages = []
        self.current_page = 0
        self.ambient_speech_cooldown = 0.0
        self.ambient_speech_timer = 0.0
        self.ambient_speaker = ""
        self.ambient_text = ""
        self.ambient_anchor = None

    @property
    def is_active(self):
        """Indicates whether a regular dialogue is in progress."""
        return self.active_dialogue is not None

    @property
    def is_ambient_active(self):
        """Indicates whether an ambient speech bubble is visible."""
        return self.ambient_speech_timer > 0

    @property
    def current_text(self):
        """Returns the current line or an empty string when no dialogue is active."""
        if not self.is_active:
            return ""

        return self.active_dialogue[self.current_line]

    def get_lines(self, dialogue_id):
        """Returns the configured lines for a dialogue identifier."""
        return tuple(
            line
            for _, lines in self.get_turns(dialogue_id)
            for line in lines
        )

    def get_turns(self, dialogue_id):
        """Returns the ordered speakers and their lines for a dialogue."""
        if dialogue_id not in self.dialogues:
            raise KeyError(f"Diálogo não encontrado: {dialogue_id}")

        dialogue = self.dialogues[dialogue_id]
        turns = [(dialogue["speaker"], tuple(dialogue["lines"]))]
        index = 2
        while f"speaker{index}" in dialogue:
            turns.append(
                (
                    dialogue[f"speaker{index}"],
                    tuple(dialogue[f"lines{index}"]),
                )
            )
            index += 1
        return tuple(turns)

    def get_speaker(self, dialogue_id):
        """Returns the speaker configured for a dialogue identifier."""
        if dialogue_id not in self.dialogues:
            raise KeyError(f"Diálogo não encontrado: {dialogue_id}")

        return self.dialogues[dialogue_id]["speaker"]

    def start(self, dialogue_id, speaker=None):
        """Starts a dialogue by identifier and prepares its first page."""
        if self.is_active:
            return False

        turns = self.get_turns(dialogue_id)
        if speaker is not None:
            turns = tuple((speaker, lines) for _, lines in turns)
        return self._start_turns(turns)

    def start_lines(self, lines, speaker=""):
        """Starts dialogue from inline text while keeping progression centralized."""
        if self.is_active:
            return False

        if isinstance(lines, str):
            lines = (lines,)
        else:
            lines = tuple(lines)
        if not lines:
            raise ValueError("O diálogo precisa conter ao menos uma fala.")

        return self._start_turns(((speaker, lines),))

    def _start_turns(self, turns):
        """Starts ordered speaker turns and flattens them for line progression."""
        lines = tuple(
            line
            for _, turn_lines in turns
            for line in turn_lines
        )
        if not lines:
            raise ValueError("O diálogo precisa conter ao menos uma fala.")

        self.active_dialogue = lines
        self.active_speakers = tuple(
            speaker
            for speaker, turn_lines in turns
            for _ in turn_lines
        )
        self.current_line = 0
        self.active_speaker = self.active_speakers[0]
        self.clear_ambient_speech()
        self._prepare_current_line()
        return True

    def handle_event(self, event):
        """Advances pages or lines in response to the dialogue confirmation key."""
        if (
            # Ignora eventos que não avançam diálogos.
            event.type != pygame.KEYDOWN
            # E é a tecla usada para continuar ou fechar a fala.
            or event.key != pygame.K_e
            # Sem diálogo ativo, não há estado a avançar.
            or not self.is_active
        ):
            return False

        if self.current_page + 1 < len(self.current_pages):
            self.current_page += 1
            return False

        return self.advance()

    def advance(self):
        """Advances to the next line and closes after the final line."""
        if not self.is_active:
            return False

        self.current_line += 1
        if self.current_line >= len(self.active_dialogue):
            self.close()
            return True

        self.active_speaker = self.active_speakers[self.current_line]
        self._prepare_current_line()
        return False

    def _prepare_current_line(self):
        """Paginates the current line and resets its page cursor."""
        self.current_pages = self.dialogue_box.paginate(self.current_text)
        self.current_page = 0

    def close(self):
        """Closes the active dialogue and clears its presentation state."""
        self.active_dialogue = None
        self.active_speakers = ()
        self.active_speaker = ""
        self.current_line = 0
        self.current_pages = []
        self.current_page = 0

    def try_start_ambient(self, nearby_npcs):
        """Applies the ambient-speech chance and cooldown to nearby NPCs."""
        # Só tenta sortear quando há NPC próximo, sem diálogo ou balão ativo.
        if (
            not nearby_npcs
            # Um diálogo normal tem prioridade sobre falas ambientais.
            or self.is_active
            # Balões ambientais também não devem se sobrepor.
            or self.is_ambient_active
        ):
            return False
        if self.ambient_speech_cooldown > 0:
            return False

        self.ambient_speech_cooldown = self.AMBIENT_SPEECH_COOLDOWN
        if random.randint(1, 100) > self.AMBIENT_SPEECH_CHANCE:
            return False

        npc = random.choice(tuple(nearby_npcs))
        self.ambient_speaker = npc.display_name
        self.ambient_text = random.choice(npc.ambient_lines)
        self.ambient_anchor = npc
        self.ambient_speech_timer = self.AMBIENT_SPEECH_DURATION
        return True

    def clear_ambient_speech(self):
        """Hides ambient speech and releases its NPC reference."""
        self.ambient_speech_timer = 0.0
        self.ambient_speaker = ""
        self.ambient_text = ""
        self.ambient_anchor = None

    def update(self, delta_time):
        """Updates ambient-speech cooldown and visibility duration."""
        self.ambient_speech_cooldown = max(
            0.0,
            self.ambient_speech_cooldown - delta_time,
        )
        self.ambient_speech_timer = max(
            0.0,
            self.ambient_speech_timer - delta_time,
        )
        if not self.is_ambient_active:
            self.clear_ambient_speech()

    def draw(self, screen):
        """Draws the active dialogue or its ambient speech bubble."""
        # Fala de diálogo tem prioridade sobre balões ambientais.
        if (
            # Só desenha a caixa normal com diálogo ativo e páginas prontas.
            self.is_active
            and self.current_pages
        ):
            self.dialogue_box.draw(
                screen,
                self.current_pages[self.current_page],
                speaker_name=self.active_speaker,
                has_next_page=(
                    self.current_page + 1 < len(self.current_pages)
                ),
            )
        # Balão ambiental exige temporizador ativo e NPC âncora válido.
        elif (
            self.is_ambient_active
            and self.ambient_anchor is not None
        ):
            self.draw_bubble(
                screen,
                self.ambient_anchor,
                f"{self.ambient_speaker}: {self.ambient_text}",
            )

    def draw_bubble(self, screen, anchor, text):
        """Draws a compact speech bubble through the dialogue presentation."""
        self.dialogue_box.draw_bubble(screen, anchor, text)

    def begin_frame(self):
        """Resets the shared bubble layout before the active scene is drawn."""
        self.dialogue_box.begin_frame()

    def stack_bubble_rect(self, rect):
        """Reserves an interaction hint rectangle in the shared bubble layout."""
        return self.dialogue_box.stack_bubble_rect(rect)
