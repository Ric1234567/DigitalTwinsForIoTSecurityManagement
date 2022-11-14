import { Zigbee2MqttConfiguration } from "./zigbee2mqttConfiguration";
import { MosquittoConfiguration } from "./mosquittoConfiguration";
import { IpConfiguration } from "./ipConfiguration";
import { OsqueryConfiguration } from "./osqueryConfiguration";

export class NetworkConfiguration {
    ip_configuration:IpConfiguration
    zigbee_2_mqtt:Zigbee2MqttConfiguration
    mosquitto:MosquittoConfiguration
    osquery:OsqueryConfiguration

    constructor(ipConfiguration: IpConfiguration, zigbee2mqttConfiguration:Zigbee2MqttConfiguration, mosquittoConfiguration:MosquittoConfiguration, osqueryConfiguration:OsqueryConfiguration) {
        this.ip_configuration = ipConfiguration
        this.zigbee_2_mqtt = zigbee2mqttConfiguration
        this.mosquitto = mosquittoConfiguration
        this.osquery = osqueryConfiguration
    }
}