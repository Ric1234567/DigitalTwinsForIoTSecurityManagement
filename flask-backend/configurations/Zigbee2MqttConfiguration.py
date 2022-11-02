class Zigbee2MqttConfiguration:
    def __init__(self):
        self.permit_join = True

    def repr_json(self):
        return dict(permit_join=self.permit_join)
