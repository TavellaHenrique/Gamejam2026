

class Inventory:

    def __init__(self):
        self.items = {}

    def add_item(self, item):
        if item.id in self.items:
            return False

        self.items[item.id] = item
        return True

    def has_item(self, item_id):
        return item_id in self.items

    def get_item(self, item_id):
        return self.items.get(item_id)

    def remove_item(self, item_id):
        return self.items.pop(item_id, None)

    def get_all_items(self):
        return list(self.items.values())