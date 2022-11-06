import string
import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.ssh.SshHandler import SshHandler


def start_osquery_scan_service(ip_address: string, ssh_port, delay: int):
    while True:
        print(
            "Get osquery information " + " (" + ip_address + "," + current_process().name + "," + str(delay) + ")")

        download_osquery_output_file(ip_address, ssh_port)
        data = read_osquery_output_file()

        database_handler = DatabaseHandler(constants.MONGO_URI)
        print("Writing result of scan to database (" + current_process().name + ")")
        database_handler.write_all_to_database(constants.OSQUERY_AND_COLLECTION_NAME_LISTENING_PORTS, data)
        database_handler.write_all_to_database(constants.OSQUERY_AND_COLLECTION_NAME_PROCESSES, data)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


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
