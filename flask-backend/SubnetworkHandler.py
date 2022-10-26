import io
import time
from multiprocessing import current_process

import yaml

import constants
from DatabaseHandler import DatabaseHandler
from SshHandler import SshHandler


class SubnetworkHandler:

    def configuration_from_yaml(self, data):
        fp = io.StringIO(data)
        return yaml.safe_load(fp)

    def scan_subnetwork(self):
        ssh_handler = SshHandler(constants.SSH_HOSTNAME, constants.SSH_PORT, constants.SSH_USER,
                                 constants.SSH_PASSWORD)
        ssh_handler.connect()
        ssh_handler.download_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME,
                                           constants.ZIGBEE2MQTT_REMOTE_FILE_PATH)
        ssh_handler.download_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME_CONFIG,
                                           constants.ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG)
        ssh_handler.disconnect()

        with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME, 'r') as file:
            data_point_string = file.read()
        data_point = eval(data_point_string)

        with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME_CONFIG, 'r') as file:
            config_string = file.read()

        # add timestamp to data_point
        data_point = {
            'unixTime': round(time.time()),
            'host': constants.SSH_HOSTNAME,  # here ip of host in ip network to which the subnetwork is connected
            'state': data_point,
            'config': config_string
        }

        # write to database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        print("Writing result of subnetwork scan to database (" + current_process().name + ")")
        database_handler.insert_one_into(constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE,
                                         data_point)

    def get_latest_subnetwork_information(self):
        database_handler = DatabaseHandler(constants.MONGO_URI)
        latest_entry = database_handler.get_latest_entry(constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE)
        subnetwork = []

        connected_subnetwork_hex = list(latest_entry['state'])
        config_file = self.configuration_from_yaml(latest_entry['config'])

        for connected_device_hex in connected_subnetwork_hex:
            tmp_dict = {
                'hex': connected_device_hex,
                'host': latest_entry['host'],
                'name': config_file['devices'][connected_device_hex]['friendly_name']
            }
            subnetwork.append(tmp_dict)

        return subnetwork, latest_entry['unixTime']
