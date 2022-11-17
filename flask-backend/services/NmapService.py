import string
import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler


# static method which starts an endless nmap scan service with given command and delay
def start_nmap_scan_service(nmap_command: string, delay: int):
    while True:
        execute_nmap_scan(nmap_command)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


# execute an nmap network scan and write results to database
def execute_nmap_scan(nmap_command: string):
    print("Performing Nmap Scan (" + nmap_command + "," + current_process().name + ")")
    nmap_handler = NmapHandler()
    nmap_report_json = nmap_handler.get_report_as_json(nmap_command)

    nmap_handler.insert_nmaprun_to_database(nmap_report_json)
