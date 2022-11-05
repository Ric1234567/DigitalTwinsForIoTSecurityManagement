import json
import string


class Recommendation:
    def __init__(self, title: string, description: string):
        self.title = title
        self.description = description

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)