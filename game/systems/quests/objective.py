from dataclasses import dataclass

@dataclass
class QuestObjective:
    objective_type: str
    target: str
    required: int = 1
    progress: int = 0

    @property
    def completed(self):
        return self.progress >= self.required

    def register(self, event_type, target, amount=1):
        """Verifica se um objetivo corresponde ao objetivo e atualiza o progresso caso corresponda"""
        if self.completed:
            return

        if self.objective_type != event_type:
            return

        if self.target != target:
            return

        self.progress = min(
            self.progress + amount,
            self.required
        )

