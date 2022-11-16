import string
import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.ssh.SshHandler import SshHandler
from handler.ssh.SshInformation import SshInformation


# static method which starts an endless osquery service with given ip, ssh port and delay time
def start_osquery_scan_service(ip_address: string, ssh_port, delay: int):
    while True:
        ssh_information = SshInformation(ip_address, ssh_port)
        execute_osquery_scan(ssh_information)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


# main method to execute an osquery can for a given ssh host
def execute_osquery_scan(ssh_information: SshInformation):
    print("Get osquery information " + " (" + ssh_information.ip + "," + current_process().name + ")")

    download_osquery_log(ssh_information.ip, ssh_information.port)
    log_data = read_osquery_log()

    if log_data == '':
        print('Nothing to save.')
        return

    print("Writing result of scan to database (" + current_process().name + ")")
    database_handler = DatabaseHandler(constants.MONGO_URI)

    # write listening_ports data to database collection
    database_handler.write_all_to_database(constants.OSQUERY_AND_COLLECTION_NAME_LISTENING_PORTS, log_data, ssh_information)

    # write usb_device data to database collection
    database_handler.write_all_to_database(constants.OSQUERY_AND_COLLECTION_NAME_USB_DEVICES, log_data, ssh_information)


# downloads the osquery log of host running ssh and osquery daemon
def download_osquery_log(ip_address, ssh_port):
    ssh_handler = SshHandler(ip_address, ssh_port, constants.SSH_USER,
                             constants.SSH_PASSWORD)
    ssh_handler.connect()

    # delete content of log to prevent saving redundant information
    ssh_handler.download_file_delete_content_via_sftp(
        constants.FILE_OUTPUT_DIRECTORY + constants.OSQUERY_DAEMON_LOCAL_OUTPUT_LOG_FILE_NAME,
        constants.OSQUERY_REMOTE_LOG_FILE_PATH)

    ssh_handler.disconnect()


# reads in the osquery log from the output dir
def read_osquery_log():
    with open(constants.FILE_OUTPUT_DIRECTORY + constants.OSQUERY_DAEMON_LOCAL_OUTPUT_LOG_FILE_NAME, 'r') as file:
        data = file.read()
    return data  # not a json
