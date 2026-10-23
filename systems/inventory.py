
class Inventory:
    """Armazena e gerencia os itens coletados pelo jogador"""

    def __init__(self):
        # Armazena os itens
        self.items = {}

    def add_item(self, item):
        """Adiciona um item ao inventário. Retorna True se o item for adicionado com sucesso e False case não seja."""
        # Verifica se o item já está armazenado
        if item.id in self.items:
            return False

        # Adiciona o item
        self.items[item.id] = item

        return True

    def has_item(self, item_id):
        """Verifica se o item já está no inventário. Busca apenas por seu ID"""
        return item_id in self.items

    def get_item(self, item_id):
        """Retorna um item do inventário"""
        return self.items.get(item_id)

    def remove_item(self, item_id):
        """Remove um item do inventário com base no ID"""
        return self.items.pop(item_id, None)

    def get_all_items(self):
        """Retorna todos os valores do inventário"""
        return list(self.items.values())