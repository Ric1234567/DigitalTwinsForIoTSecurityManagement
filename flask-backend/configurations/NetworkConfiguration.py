import json

from util.ComplexJsonEncoder import ComplexJsonEncoder
from configurations.Zigbee2MqttConfiguration import Zigbee2MqttConfiguration


class NetworkConfiguration:
    def __init__(self):
        self.zigbee_2_mqtt: Zigbee2MqttConfiguration = Zigbee2MqttConfiguration()

    def repr_json(self):
        return dict(zigbee_2_mqtt=self.zigbee_2_mqtt)

    def to_json(self):
        return json.dumps(self.repr_json(), cls=ComplexJsonEncoder)




