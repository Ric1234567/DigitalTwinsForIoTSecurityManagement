import string

from analysis import SecurityIssueTypes
from analysis.ip.IpIssueSolver import IpIssueSolver
from analysis.mosquitto.MosquittoIssueSolver import MosquittoIssueSolver
from analysis.zigbee2Mqtt.Zigbee2MqttIssueSolver import Zigbee2MqttIssueSolver


# Provides the solving of found security issues by the network configuration.
class HostSolver:
    def __init__(self, configuration):
        self.configuration = configuration

    # Main method to use HostSolver.
    def solve(self, host_ip: string, issue_type: string):
        result = None

        # identify issue by issue type string
        if issue_type == SecurityIssueTypes.ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME:
            solver = Zigbee2MqttIssueSolver(self.configuration['zigbee_2_mqtt'])
            result = solver.fix_permit_join(host_ip)
        elif issue_type == SecurityIssueTypes.MOSQUITTO_ACCESS_CONTROL_LIST:
            solver = MosquittoIssueSolver(self.configuration['mosquitto'])
            result = solver.fix_access_control_list(host_ip)
        elif issue_type == SecurityIssueTypes.IP_TOO_MANY_OPEN_PORTS:
            solver = IpIssueSolver(self.configuration['ip_configuration'])
            result = solver.fix_too_many_open_ports(host_ip)

        return result
