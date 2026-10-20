
class Scene:
    def __init__(self, game):
        self.game = game

    # Deve lidar com os eventos de teclados, mouse e afins
    def handle_events(self, event):
        pass

    # Atualiza movimento, animações e lógica da cena
    def update(self, delta_time):
        pass

    # Desenha o cenário e seus elementos
    def draw(self, screen):
        pass

    # Prepara a cena quando ela é chamada (se torna ativa)
    def on_enter(self):
        pass

    # Libera recursos ou encerra algo, se necessário
    def on_exit(self):
        pass