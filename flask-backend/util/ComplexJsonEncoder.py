import json


# Encoder class for encoding python objects to json which implement a 'repr_json' method
class ComplexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)
