import { Zigbee2MqttConfiguration } from "./zigbee2mqttConfiguration";
import { MosquittoConfiguration } from "./mosquittoConfiguration";
import { IpConfiguration } from "./ipConfiguration";

export class NetworkConfiguration {
    ip_configuration:IpConfiguration
    zigbee_2_mqtt:Zigbee2MqttConfiguration
    mosquitto:MosquittoConfiguration

    constructor(ipConfiguration: IpConfiguration, zigbee2mqttConfiguration:Zigbee2MqttConfiguration, mosquittoConfiguration:MosquittoConfiguration) {
        this.ip_configuration = ipConfiguration
        this.zigbee_2_mqtt = zigbee2mqttConfiguration
        this.mosquitto = mosquittoConfiguration
    }
}