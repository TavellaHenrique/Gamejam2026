class QuestManager:
    def __init__(self, quests=None):
        self.quests = {
            quest.quest_id: quest
            for quest in (quests or [])
        }

    def start_quest(self, quest_id):
        quest = self.quests.get(quest_id)

        if quest is None:
            return False

        return quest.start()

    def unlock_quest(self, quest_id):
        quest = self.quests.get(quest_id)

        if quest is None:
            return False

        return quest.unlock()

    def register_event(self, event_type, target, amount=1):
        """Verifica se o evento corresponde a algum objetivo de qualquer missão"""
        for quest in self.quests.values():
            quest.register_event(
                event_type,
                target,
                amount
            )

    def get_status(self, quest_id):
        quest = self.quests.get(quest_id)

        if quest is None:
            return None

        return quest.status

    def is_completed(self, quest_id):
        from game.systems.quests.quest_status import QuestStatus

        return (
            self.get_status(quest_id)
            == QuestStatus.COMPLETED
        )