import string

from handler.HostInformation import HostInformation

IP_TOO_MANY_OPEN_PORTS = 'ip_too_many_open_ports'
ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME = 'zigbee2mqtt_permit_join'
MOSQUITTO_ACCESS_CONTROL_LIST = 'mosquitto_access_control_list'
OSQUERY_CONNECTED_USBS = 'unkown_connected_usbs'


def is_fixable(issue_type: string, host: HostInformation):
    if issue_type == IP_TOO_MANY_OPEN_PORTS or \
            issue_type == ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME or \
            issue_type == MOSQUITTO_ACCESS_CONTROL_LIST:
        if host.ssh_information is None:
            return False
        else:
            return True

    return False
