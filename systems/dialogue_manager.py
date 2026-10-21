import json
import random

import pygame

from ui.dialogue_box import DialogueBox


class DialogueManager:
    """Controls dialogue state, progression, ambient speech, and presentation."""

    AMBIENT_SPEECH_CHANCE = 30
    AMBIENT_SPEECH_COOLDOWN = 8.0
    AMBIENT_SPEECH_DURATION = 3.0

    def __init__(self, dialogues_path):
        """Loads dialogue data and initializes the dialogue presentation."""
        with open(dialogues_path, "r", encoding="utf-8") as file:
            self.dialogues = json.load(file)

        self.dialogue_box = DialogueBox()
        self.active_dialogue = None
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
        if dialogue_id not in self.dialogues:
            raise KeyError(f"Diálogo não encontrado: {dialogue_id}")

        return tuple(self.dialogues[dialogue_id])

    def start(self, dialogue_id, speaker=""):
        """Starts a dialogue by identifier and prepares its first page."""
        if self.is_active:
            return False

        return self.start_lines(self.get_lines(dialogue_id), speaker=speaker)

    def start_lines(self, lines, speaker=""):
        """Starts dialogue from inline text while keeping progression centralized."""
        if self.is_active:
            return False

        if isinstance(lines, str):
            lines = (lines,)
        if not lines:
            raise ValueError("O diálogo precisa conter ao menos uma fala.")

        self.active_dialogue = tuple(lines)
        self.current_line = 0
        self.active_speaker = speaker
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

        self._prepare_current_line()
        return False

    def _prepare_current_line(self):
        """Paginates the current line and resets its page cursor."""
        self.current_pages = self.dialogue_box.paginate(self.current_text)
        self.current_page = 0

    def close(self):
        """Closes the active dialogue and clears its presentation state."""
        self.active_dialogue = None
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
