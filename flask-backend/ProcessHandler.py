#!/usr/bin/python3
import time
from multiprocessing import active_children, current_process

from flask_pymongo import MongoClient

from DatabaseHandler import DatabaseHandler
from NmapHandler import NmapHandler

process_dict = {}


def get_processes():
    return active_children()


def get_process_by_name(name):
    processes = active_children()
    for process in processes:
        if process.name == name:
            return process
    # no match
    return None


def endless_network_scan(mongo_uri, nmap_command, delay):
    while True:
        print("Performing Network Scan (" + nmap_command + "," + current_process().name + "," + str(delay) + ")")
        nmap_handler = NmapHandler()
        nmap_report_json = nmap_handler.get_report_as_json(nmap_command)

        print("Writing result of scan to database (" + current_process().name + ")")
        database_handler = DatabaseHandler(mongo_uri)
        database_handler.write_nmaprun_to_database(nmap_report_json)

        print(current_process().name + " Sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)
