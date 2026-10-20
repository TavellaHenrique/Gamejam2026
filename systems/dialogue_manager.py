
import json

class DialogueManager:

    def __init__(self, dialogues_path):
        with open(dialogues_path, "r", encoding="utf-8") as file:
            self.dialogues = json.load(file)

        self.active_dialogue = None
        self.current_line = 0

    @property
    def is_active(self):
        return self.active_dialogue is not None

    def start(self, dialogue_id):
        if self.is_active:
            return

        if dialogue_id not in self.dialogues:
            raise KeyError(
                f"Diálogo não encontrado: {dialogue_id}"
            )

        self.active_dialogue = self.dialogues[dialogue_id]
        self.current_line = 0

    @property
    def current_text(self):
        if not self.is_active:
            return ""

        return self.active_dialogue[self.current_line]

    def advance(self):
        if not self.is_active:
            return

        self.current_line += 1

        if self.current_line >= len(self.active_dialogue):
            self.close()

    def close(self):
        self.active_dialogue = None
        self.current_line = 0
