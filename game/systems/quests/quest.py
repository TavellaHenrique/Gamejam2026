from dataclasses import dataclass, field

from game.systems.quests.objective import QuestObjective
from game.systems.quests.quest_status import QuestStatus

@dataclass
class Quest:
    quest_id: str
    name: str
    objectives: list[QuestObjective]

    status: QuestStatus = QuestStatus.AVAIABLE

    def unlock(self):
        if self.status != QuestStatus.LOCKED:
            return False

        self.status = QuestStatus.AVAIABLE
        return True

    def start(self):
        if self.status != QuestStatus.AVAIABLE:
            return False

        self.status = QuestStatus.ACTIVE
        return True

    def register_event(self, event_type, target, amount=1):
        """Verifica se um evento foi concluído e atualiza seu status"""
        if self.status != QuestStatus.ACTIVE:
            return

        for objective in self.objectives:
            objective.register(event_type, target, amount)

        if self.is_completed:
            self.status = QuestStatus.COMPLETED

    @property
    def is_completed(self):
        """Retorna True caso todos os objetivos da missão estejam concluídos"""
        return all(objective.completed for objective in self.objectives)
