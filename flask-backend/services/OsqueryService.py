import json
import string
import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.ssh.SshHandler import SshHandler
from handler.ssh.SshInformation import SshInformation


def start_osquery_scan_service(ip_address: string, ssh_port, delay: int):
    while True:
        ssh_information = SshInformation(ip_address, ssh_port)
        get_osquery_data(ssh_information)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


def get_osquery_data(ssh_information: SshInformation):
    print(
        "Get osquery information " + " (" + ssh_information.ip + "," + current_process().name + ")")

    download_osquery_output_file(ssh_information.ip, ssh_information.port)
    data = read_osquery_output_file()

    if data == '':
        print('Nothing to save.')
        return

    print("Writing result of scan to database (" + current_process().name + ")")
    database_handler = DatabaseHandler(constants.MONGO_URI)
    database_handler.write_all_to_database(constants.OSQUERY_AND_COLLECTION_NAME_LISTENING_PORTS, data, ssh_information)
    database_handler.write_all_to_database(constants.OSQUERY_AND_COLLECTION_NAME_USB_DEVICES, data, ssh_information)


def download_osquery_output_file(ip_address, ssh_port):
    ssh_handler = SshHandler(ip_address, ssh_port, constants.SSH_USER,
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
