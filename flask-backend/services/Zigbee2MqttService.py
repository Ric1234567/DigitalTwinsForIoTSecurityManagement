import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from handler.SubnetworkHandler import SubnetworkHandler
from handler.ssh.SshInformation import SshInformation


# static method which starts an endless zigbee2mqtt service with a given delay time
def start_zigbee2mqtt_network_state_service(delay: int):
    while True:
        execute_zigbee2mqtt_scan()

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


def execute_zigbee2mqtt_scan(ssh_information: SshInformation):
    print("Get zigbee2mqtt network state " + " (" + current_process().name + ")")

    subnetwork_handler = SubnetworkHandler()
    subnetwork_handler.scan_subnetwork_host(ssh_information)
