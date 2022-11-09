import string
import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler


def start_nmap_scan_service(nmap_command: string, delay: int):
    while True:
        get_nmap_data(nmap_command)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


def get_nmap_data(nmap_command: string):
    print("Performing Nmap Scan (" + nmap_command + "," + current_process().name + ")")
    nmap_handler = NmapHandler()
    nmap_report_json = nmap_handler.get_report_as_json(nmap_command)

    print("Writing result of nmap scan to database (" + current_process().name + ")")
    database_handler = DatabaseHandler(constants.MONGO_URI)
    database_handler.write_nmaprun_to_database(nmap_report_json)
