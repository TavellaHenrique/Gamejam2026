
"""Define a interface comum que as cenas do jogo devem implementar."""


class Scene:
    """Classe-base para cenas que recebem eventos e controlam a própria exibição."""

    def __init__(self, game):
        """Guarda a instância do jogo para acesso ao estado compartilhado."""
        self.game = game

    def is_inventory_open(self):
        """Indica se o inventário está aberto e deve pausar a interação do mundo."""
        return bool(getattr(self.game, "inventory_open", False))

    @property
    def is_paused(self):
        """Indica se uma interface modal pausa a simulação desta cena."""
        return False

    # Deve lidar com os eventos de teclados, mouse e afins
    def handle_event(self, event):
        """Ponto de extensão para processar eventos recebidos pela cena."""
        if self.is_inventory_open():
            return

    # Atualiza movimento, animações e lógica da cena
    def update(self, delta_time):
        """Ponto de extensão para atualizar a lógica usando o tempo decorrido."""
        pass

    # Desenha o cenário e seus elementos
    def draw(self, screen):
        """Ponto de extensão para desenhar a cena na superfície fornecida."""
        pass

    # Prepara a cena quando ela é chamada (se torna ativa)
    def on_enter(self):
        """Ponto de extensão chamado quando a cena se torna ativa."""
        pass

    # Libera recursos ou encerra algo, se necessário
    def on_exit(self):
        """Ponto de extensão chamado antes de a cena ativa ser substituída."""
        pass