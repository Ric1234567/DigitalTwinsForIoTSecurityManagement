#!/usr/bin/python3
import numbers
import string
import time
from multiprocessing import active_children, current_process, Process

from flask_pymongo import MongoClient

import constants
from DatabaseHandler import DatabaseHandler
from NmapHandler import NmapHandler
from SshHandler import SshHandler

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


def start_process(process_name: string, target, args: tuple):
    service_process = Process(name=process_name,
                              target=target,
                              args=args)
    service_process.start()
    process_dict[service_process.pid] = service_process
    print("Start process " + service_process.name)
    return service_process


def endless_network_scan(mongo_uri: string, nmap_command: string, delay: numbers):
    while True:
        print("Performing Network Scan (" + nmap_command + "," + current_process().name + "," + str(delay) + ")")
        nmap_handler = NmapHandler()
        nmap_report_json = nmap_handler.get_report_as_json(nmap_command)

        print("Writing result of scan to database (" + current_process().name + ")")
        database_handler = DatabaseHandler(mongo_uri)
        database_handler.write_nmaprun_to_database(nmap_report_json)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


def endless_osquery_scan(ip_address: string, delay: numbers):
    while True:
        print("Get osquery information " + " (" + ip_address + "," + current_process().name + "," + str(delay) + ")")

        download_osquery_output_file()
        data = read_osquery_output_file()

        database_handler = DatabaseHandler(constants.MONGO_URI)
        print("Writing result of scan to database (" + current_process().name + ")")
        database_handler.write_all_to_database(constants.OSQUERY_AND_COLLECTION_NAME_LISTENING_PORTS, data)
        database_handler.write_all_to_database(constants.OSQUERY_AND_COLLECTION_NAME_PROCESSES, data)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


def download_osquery_output_file():
    ssh_handler = SshHandler(constants.SSH_HOSTNAME, constants.SSH_PORT, constants.SSH_USER,
                             constants.SSH_PASSWORD)
    ssh_handler.connect()
    ssh_handler.download_file_delete_content_via_sftp(
        constants.FILE_OUTPUT_DIRECTORY + constants.OSQUERY_DAEMON_LOCAL_OUTPUT_LOG_FILE_NAME,
        constants.OSQUERY_REMOTE_LOG_FILE_PATH)
    ssh_handler.disconnect()


def read_osquery_output_file():
    with open(constants.FILE_OUTPUT_DIRECTORY + constants.OSQUERY_DAEMON_LOCAL_OUTPUT_LOG_FILE_NAME, 'r') as file:
        data = file.read()
    return data  # not a json


def endless_get_zigbee2mqtt_network_state(delay: numbers):
    while True:
        print(
            "Get zigbee2mqtt network state " + " (" + constants.SSH_HOSTNAME + "," + current_process().name + "," + str(
                delay) + ")")
        ssh_handler = SshHandler(constants.SSH_HOSTNAME, constants.SSH_PORT, constants.SSH_USER,
                                 constants.SSH_PASSWORD)
        ssh_handler.connect()
        ssh_handler.download_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME,
                                           constants.ZIGBEE2MQTT_REMOTE_FILE_PATH)

        with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME, 'r') as file:
            data_point_string = file.read()
        data_point = eval(data_point_string)

        # add timestamp to data_point
        data_point = {
            'unixTime': round(time.time()),
            'state': data_point
        }

        # write to database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        print("Writing result of scan to database (" + current_process().name + ")")
        database_handler.insert_one_into(constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE,
                                         data_point)
        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)
