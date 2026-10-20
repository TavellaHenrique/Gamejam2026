
import json


class DialogueManager:
    """Carrega falas e controla qual diálogo e linha estão ativos."""

    def __init__(self, dialogues_path):
        """Lê as falas do arquivo JSON e inicializa sem diálogo ativo."""
        with open(dialogues_path, "r", encoding="utf-8") as file:
            self.dialogues = json.load(file)

        self.active_dialogue = None
        self.current_line = 0

    @property
    def is_active(self):
        """Indica se existe um diálogo em andamento."""
        return self.active_dialogue is not None

    def start(self, dialogue_id):
        """Inicia um diálogo pelo identificador ou levanta erro se não existir."""
        # Não substitui uma conversa que já esteja em andamento.
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
        """Retorna a fala atual ou uma string vazia quando não há diálogo."""
        if not self.is_active:
            return ""

        return self.active_dialogue[self.current_line]

    def advance(self):
        """Avança uma linha e fecha o diálogo depois da última fala."""
        if not self.is_active:
            return

        self.current_line += 1

        # Ao ultrapassar o último índice, reinicia o estado do diálogo.
        if self.current_line >= len(self.active_dialogue):
            self.close()

    def close(self):
        """Limpa a fala ativa e reinicia o índice para a próxima conversa."""
        self.active_dialogue = None
        self.current_line = 0
