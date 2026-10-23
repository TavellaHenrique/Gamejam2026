from systems.quests.quest import Quest
from systems.quests.objective import QuestObjective

def create_quests():
    return [
        Quest(
            quest_id="find_the_key",
            name="Encontre a chave do Laboratório 7",
            objectives=[
                QuestObjective(
                    "collect_item",
                    "lab_key",
                ),
                QuestObjective(
                    "return_item",
                    "lab_key",
                ),
            ],
        ),
    ]