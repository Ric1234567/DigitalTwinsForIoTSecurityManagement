import string
import time
from multiprocessing import current_process

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.ssh.SshHandler import SshHandler


def start_mosquitto_service(ip_address: string, ssh_port: int, delay: int):
    while True:
        print("Get mosquitto configuration data (" + ip_address + "," + current_process().name + "," + str(delay) + ")")
        download_mosquitto_config_files(ip_address, ssh_port)

        with open(constants.FILE_OUTPUT_DIRECTORY + constants.MOSQUITTO_FILE_NAME_CONFIG, 'r') as file:
            config_content = file.read()

        with open(constants.FILE_OUTPUT_DIRECTORY + constants.MOSQUITTO_FILE_NAME_ACL, 'r') as file:
            acl_content = file.read()

        data = {
            'unixTime': round(time.time()),
            'host': ip_address,
            'config': config_content,
            'acl': acl_content
        }

        # write to database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        print("Writing mosquitto config to database (" + current_process().name + ")")
        database_handler.insert_one_into(constants.COLLECTION_NAME_MOSQUITTO_CONFIG, data)

        print(current_process().name + " sleeping for " + str(delay) + " seconds!")
        time.sleep(delay)


def download_mosquitto_config_files(ip: string, ssh_port: int):
    ssh_handler = SshHandler(ip, ssh_port, constants.SSH_USER, constants.SSH_PASSWORD)
    ssh_handler.connect()
    # download config file
    ssh_handler.download_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + constants.MOSQUITTO_FILE_NAME_CONFIG,
                                       constants.MOSQUITTO_REMOTE_CONFIG_DIR_PATH +
                                       constants.MOSQUITTO_REMOTE_CONFIG_FILE_NAME)
    # download acl file
    ssh_handler.download_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + constants.MOSQUITTO_FILE_NAME_ACL,
                                       constants.MOSQUITTO_REMOTE_CONFIG_DIR_PATH +
                                       constants.MOSQUITTO_REMOTE_ACL_FILE_NAME)
    ssh_handler.disconnect()