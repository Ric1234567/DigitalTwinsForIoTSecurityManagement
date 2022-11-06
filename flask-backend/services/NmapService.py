import string
import time
from multiprocessing import current_process

from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler


def start_nmap_scan_service(mongo_uri: string, nmap_command: string, delay: int):
    while True:
        print("Performing Nmap Scan (" + nmap_command + "," + current_process().name + "," + str(delay) + ")")
        nmap_handler = NmapHandler()
        nmap_report_json = nmap_handler.get_report_as_json(nmap_command)

        print("Writing result of nmap scan to database (" + current_process().name + ")")
        database_handler = DatabaseHandler(mongo_uri)
        database_handler.write_nmaprun_to_database(nmap_report_json)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)
