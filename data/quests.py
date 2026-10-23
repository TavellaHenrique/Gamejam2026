from systems.quests.quest import Quest
from systems.quests.objective import QuestObjective

def create_quests():
    return [
        Quest(
            quest_id="test_quest",
            name="Missão de Teste",
            objectives=[
                QuestObjective(
                    "collect_item",
                    "lab_key"
                ),
                QuestObjective(
                    "talk_to",
                    "thiago"
                ),
            ],
        ),
    ]