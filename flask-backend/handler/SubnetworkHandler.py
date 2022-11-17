import time
from multiprocessing import current_process

from handler.ssh.SshInformation import SshInformation
from util import ConfigurationHelper
import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.ssh.SshHandler import SshHandler


# class which handles (zigbee/mqtt) subnetwork data
class SubnetworkHandler:
    def __init__(self):
        self.database = DatabaseHandler(constants.MONGO_URI) \
            .mongo[constants.PI_DATABASE_NAME][constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE]

    # scan a given ssh host for subnetworks.
    # It reads the information from the zigbee2mqtt configuration and its state.json
    def scan_subnetwork_host(self, ssh_information: SshInformation):
        ssh_handler = SshHandler(ssh_information.ip, ssh_information.port, constants.SSH_USER,
                                 constants.SSH_PASSWORD)
        ssh_handler.connect()

        # download zigbee2mqtt state.json (holds information of connected devices via zigbee)
        ssh_handler.download_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME,
                                           constants.ZIGBEE2MQTT_REMOTE_FILE_PATH)

        # download zigbee2mqtt configuration.yaml file which holds naming information of connected devices
        ssh_handler.download_file_via_sftp(
            constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME_CONFIG,
            constants.ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG)

        ssh_handler.disconnect()

        # read state.json file from output file dir
        with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME, 'r') as file:
            data_point_string = file.read()
        data_point = eval(data_point_string)

        # read configuration.yaml file from output file dir
        with open(constants.FILE_OUTPUT_DIRECTORY + constants.ZIGBEE2MQTT_FILE_NAME_CONFIG, 'r') as file:
            config_string = file.read()

        config = ConfigurationHelper.parse_yaml_configuration_string(config_string)

        # build subnetwork object
        subnetwork = {
            'unixTime': round(time.time()),
            'host': ssh_information.ip,
            'state': data_point,
            'config': config
        }

        # write subnetwork information to database
        print("Writing result of subnetwork scan to database (" + current_process().name + ")")
        self.database.insert_one(subnetwork)

    # gets the latest subnetwork information from database
    def get_latest_subnetwork_information(self):
        # get latest entry
        distinct_hosts_with_subnetworks = self.database.distinct('host')

        subnetwork = []
        unix_time = -1
        # build subnetwork object with timestamp
        for host_ip in distinct_hosts_with_subnetworks:
            entries = self.database.find({'host': host_ip}).sort('unixTime', -1).limit(1)
            for entry in entries:  # just a single entry
                if unix_time < entry['unixTime']:
                    unix_time = entry['unixTime']

                connected_subnetwork_hex = list(entry['state'])
                config_file = entry['config']

                for connected_device_hex in connected_subnetwork_hex:
                    tmp_dict = {
                        'hex': connected_device_hex,
                        'host': entry['host'],
                        'name': config_file['devices'][connected_device_hex]['friendly_name']
                    }
                    subnetwork.append(tmp_dict)
                break

        return subnetwork, unix_time
