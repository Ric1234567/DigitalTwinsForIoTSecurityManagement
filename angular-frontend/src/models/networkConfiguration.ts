import { Zigbee2MqttConfiguration } from "./zigbee2mqttConfiguration";

export class NetworkConfiguration {
    zigbee_2_mqtt:Zigbee2MqttConfiguration

    constructor(zigbee2mqttConfiguration:Zigbee2MqttConfiguration) {
        this.zigbee_2_mqtt = zigbee2mqttConfiguration
    }
}