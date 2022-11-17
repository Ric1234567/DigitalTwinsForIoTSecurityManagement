import string
import time
from multiprocessing import current_process

import app
import constants
from handler.NmapHandler import NmapHandler
from handler.ssh.SshInformation import SshInformation
from services import MosquittoService, OsqueryService, NmapService, Zigbee2MqttService


# static method which starts an endless full network scan with a given nmap command and its execution delay
def start_full_network_scan_service(nmap_command: string, delay: int):
    while True:
        execute_full_network_scan(nmap_command)

        # sleep for the delay time
        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


def execute_full_network_scan(nmap_command: string):
    # execute nmap scan which gets written to the database
    NmapService.execute_nmap_scan(nmap_command)

    # get network scan from database
    nmap_report_db = app.database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    # find ssh hosts
    nmap_handler = NmapHandler()
    ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

    # execute other service operations
    for ssh_information in ssh_hosts:
        execute_all_service_scans(ssh_information)


def execute_all_service_scans(ssh_information: SshInformation):
    MosquittoService.execute_mosquitto_scan(ssh_information)
    OsqueryService.execute_osquery_scan(ssh_information)
    Zigbee2MqttService.execute_zigbee2mqtt_scan(ssh_information)

