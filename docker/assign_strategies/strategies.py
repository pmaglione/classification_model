import random

class AssignStrategy():
    def get_assignment(self, worker_id, items):
        pass

class RandomStrategy(AssignStrategy):
    def get_assignment(self, worker_id, items):
        assignable_items = [item for item in items if worker_id not in item['votes'].keys()]

        return random.choice(assignable_items)