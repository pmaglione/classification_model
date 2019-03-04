import jsonify

class Item():
    STATE_FREE = "FREE"
    STATE_ASSIGNED = "ASSIGNED"
    STATE_FINISHED = "FINISHED"

    def __init__(self, job_id, item_id, attributes_names, item_values):
        self.job_id = job_id
        self.internal_id = item_id
        self.attributes_names = attributes_names
        self.values = item_values
        self.votes = {} #votes = {worker_id: vote,...}
        self.state = self.STATE_FREE

class CrowdJob():
    def __init__(self, mongo, job_id):
        self.mongo = mongo
        self.job_id = job_id

    def create_items(self, attributes_names, items_values):
        items = []
        for item_id, item_values in enumerate(items_values):
            attrs = [attr_name for attr_name in attributes_names]
            vals = [val for val in item_values]
            item = Item(self.job_id, item_id, attrs, vals)
            items.append(item.__dict__)

        self.mongo.db.items.insert_many(items)

        return items

    def get_item_by_id(self, internal_id):
        return self.mongo.db.items.find_one({'job_id': self.job_id, "internal_id": internal_id})

    def get_items_by_state(self, state):
        return self.mongo.db.items.find({'job_id': self.job_id, "state": state})

    def update_item_votes(self, internal_id, votes):
        self.mongo.db.items.update_one({'job_id': self.job_id, 'internal_id': internal_id}, {"$set": {'votes':votes}}, upsert=False)

    def free_item(self, internal_id):
        self.mongo.db.items.update_one({'job_id': self.job_id, 'internal_id': internal_id}, {"$set": {'state': Item.STATE_FREE}}, upsert=False)

    def assign_item(self, internal_id):
        self.mongo.db.items.update_one({'job_id': self.job_id, 'internal_id': internal_id}, {"$set": {'state': Item.STATE_ASSIGNED}}, upsert=False)

    def finish_item(self, internal_id):
        self.mongo.db.items.update_one({'job_id': self.job_id, 'internal_id': internal_id}, {"$set": {'state': Item.STATE_FINISHED}}, upsert=False)

