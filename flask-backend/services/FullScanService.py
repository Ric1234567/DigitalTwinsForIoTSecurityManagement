import string
import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from handler.SubnetworkHandler import SubnetworkHandler


def start_full_network_scan_service(mongo_uri: string, nmap_command: string, delay: int):
    while True:
        # nmap
        print("Performing Full Network Scan (" + nmap_command + "," + current_process().name + "," + str(delay) + ")")
        nmap_handler = NmapHandler()
        nmap_report_json = nmap_handler.get_report_as_json(nmap_command)

        print("Writing result of nmap scan to database (" + current_process().name + ")")
        database_handler = DatabaseHandler(mongo_uri)
        database_handler.write_nmaprun_to_database(nmap_report_json)

        # get from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

        # subnetwork
        subnetwork_handler = SubnetworkHandler()
        subnetwork_handler.scan_subnetwork(ssh_hosts)

        # todo do other scanning things (get zigbee2mqtt config etc.)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)
