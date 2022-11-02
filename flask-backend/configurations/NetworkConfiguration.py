import json

from configurations.Zigbee2MqttConfiguration import Zigbee2MqttConfiguration


class NetworkConfiguration:
    def __init__(self):
        self.zigbee_2_mqtt: Zigbee2MqttConfiguration = Zigbee2MqttConfiguration()

    def repr_json(self):
        return dict(zigbee_2_mqtt=self.zigbee_2_mqtt)

    def to_json(self):
        return json.dumps(self.repr_json(), cls=ComplexEncoder)


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)


