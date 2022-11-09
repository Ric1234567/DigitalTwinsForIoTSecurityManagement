import string
import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from services import MosquittoService, OsqueryService, NmapService, Zigbee2MqttService


def start_full_network_scan_service(nmap_command: string, delay: int):
    while True:
        # nmap
        NmapService.get_nmap_data(nmap_command)

        # get from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        nmap_handler = NmapHandler()
        ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

        for ssh_information in ssh_hosts:
            MosquittoService.get_mosquitto_data(ssh_information)
            OsqueryService.get_osquery_data(ssh_information)
            Zigbee2MqttService.get_zigbee2mqtt_data()

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)
