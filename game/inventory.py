class CInventory(dict):
    def __init__(self):
        super().__init__()

        self.slot_limit = 96
        self.items = {str(i) for i in range(1, 97)}

    def add(self, slot, item):
        self.items[str(slot)] = item
    
    # def remove(self, slot):
    #     return dict.