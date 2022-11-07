import { Zigbee2MqttConfiguration } from "./zigbee2mqttConfiguration";
import { MosquittoConfiguration } from "./mosquittoConfiguration";

export class NetworkConfiguration {
    zigbee_2_mqtt:Zigbee2MqttConfiguration
    mosquitto:MosquittoConfiguration

    constructor(zigbee2mqttConfiguration:Zigbee2MqttConfiguration, mosquittoConfiguration:MosquittoConfiguration) {
        this.zigbee_2_mqtt = zigbee2mqttConfiguration
        this.mosquitto = mosquittoConfiguration
    }
}