import time
from multiprocessing import current_process

import ConfigurationHelper
import constants
from DatabaseHandler import DatabaseHandler
from ssh.SshHandler import SshHandler


class SubnetworkHandler:
    def scan_subnetwork(self, ssh_hosts):
        all_subnetworks = []
        for ssh_host in ssh_hosts:
            ipv4_address = None
            for address in ssh_host['host_address']:
                if address['@addrtype'] == 'ipv4':
                    ipv4_address = address['@addr']
            port = ssh_host['port']['@portid']

            if (ipv4_address is not None) and (port is not None):
                ssh_handler = SshHandler(ipv4_address, port, constants.SSH_USER,
                                         constants.SSH_PASSWORD)
                ssh_handler.connect()
                ssh_handler.download_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME,
                                                   constants.ZIGBEE2MQTT_REMOTE_FILE_PATH)
                ssh_handler.download_file_via_sftp(
                    constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME_CONFIG,
                    constants.ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG)
                ssh_handler.disconnect()

                with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME, 'r') as file:
                    data_point_string = file.read()
                data_point = eval(data_point_string)

                with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME_CONFIG, 'r') as file:
                    config_string = file.read()

                config = ConfigurationHelper.from_yaml_configuration(config_string)

                subnetwork = {
                    'host': ipv4_address,
                    'state': data_point,
                    'config': config
                }
                all_subnetworks.append(subnetwork)

        subnetwork_scan = {
            'unixTime': round(time.time()),
            'scans': all_subnetworks
        }

        # write to database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        print("Writing result of subnetwork scan to database (" + current_process().name + ")")
        database_handler.insert_one_into(constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE,
                                         subnetwork_scan)

    def get_latest_subnetwork_information(self):
        database_handler = DatabaseHandler(constants.MONGO_URI)
        latest_entry = database_handler.get_latest_entry(constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE)
        subnetwork = []

        if 'scans' in latest_entry:
            for scan in latest_entry['scans']:
                connected_subnetwork_hex = list(scan['state'])
                config_file = scan['config']

                for connected_device_hex in connected_subnetwork_hex:
                    tmp_dict = {
                        'hex': connected_device_hex,
                        'host': scan['host'],
                        'name': config_file['devices'][connected_device_hex]['friendly_name']
                    }
                    subnetwork.append(tmp_dict)

        return subnetwork, latest_entry['unixTime']
