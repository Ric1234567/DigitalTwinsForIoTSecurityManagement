import string
import time
from multiprocessing import current_process, Process

from handler.SubnetworkHandler import SubnetworkHandler
from handler.ssh.SshInformation import SshInformation
from services.Service import Service


# Service which runs in an endless manner.
# Performs a zigbee2mqtt scan by getting the state.json file via ssh.
class Zigbee2MqttScanService(Service):
    def __init__(self, name: string, description: string, args: tuple):
        process = Process(name=name,
                          target=self.start_zigbee2mqtt_network_state_service,
                          args=args)
        super().__init__(name, description, args, process)

    # static method which starts an endless zigbee2mqtt service with a given delay time
    def start_zigbee2mqtt_network_state_service(self, ip_address: string, ssh_port: int, delay: int):
        ssh_information = SshInformation(ip_address, ssh_port)
        while True:
            execute_zigbee2mqtt_scan(ssh_information)

            print(current_process().name + " sleeping for " + str(delay) + " seconds!")
            time.sleep(delay)


def execute_zigbee2mqtt_scan(ssh_information: SshInformation):
    print("Get zigbee2mqtt network state " + " (" + current_process().name + ")")

    subnetwork_handler = SubnetworkHandler()
    subnetwork_handler.scan_subnetwork_host(ssh_information)
