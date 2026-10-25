from game.systems.quests.quest import Quest
from game.systems.quests.objective import QuestObjective
from game.systems.quests.quest_status import QuestStatus

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
            status=QuestStatus.LOCKED,
        ),
        Quest(
            quest_id="find_the_pendrive",
            name="Encontre o pen-drive da Professora Amélia",
            objectives=[
                QuestObjective(
                    "collect_item",
                    "professora_pendrive",
                ),
                QuestObjective(
                    "return_item",
                    "professora_pendrive",
                ),
            ],
            status=QuestStatus.LOCKED,
        ),
        Quest(
            quest_id="eat_snacks",
            name="Comer salgadinho",
            objectives=[
                QuestObjective(
                    "interact_with",
                    "cantina_vending_machine",
                ),
            ],
            status=QuestStatus.LOCKED,
        ),
        Quest(
            quest_id="find_lost_necklace",
            name="Encontrar Colar Perdido",
            objectives=[
                QuestObjective(
                    "collect_item",
                    "lost_necklace",
                ),
                QuestObjective(
                    "report_item",
                    "lost_necklace",
                ),
            ],
            status=QuestStatus.LOCKED,
        ),
    ]