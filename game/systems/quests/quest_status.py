from enum import Enum, auto

class QuestStatus(Enum):
    LOCKED = auto() # missão ainda depende de um evento da história
    AVAIABLE = auto() # missão pode ser iniciada
    ACTIVE = auto() # missão está em andamento
    COMPLETED = auto() # todos os objetivos foram cumpridos