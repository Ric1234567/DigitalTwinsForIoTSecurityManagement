import string

import ConfigurationHelper
import constants
from DatabaseHandler import DatabaseHandler
from NmapHandler import NmapHandler
from analysis import SecurityIssueTypes
from ssh.SshHandler import SshHandler


class Zigbee2MqttIssueSolver:
    def __init__(self, configuration):
        self.configuration = configuration

    def fix_permit_join(self, ip: string):
        # get from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        nmap_handler = NmapHandler()
        ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

        ssh_information = None
        for ssh_host in ssh_hosts:
            for address in ssh_host['host_address']:
                if address['@addr'] == ip:
                    ssh_information = nmap_handler.get_ssh_information(ssh_host)

        # get configuration content from host
        ssh_handler = SshHandler(ssh_information.ip, ssh_information.port,
                                 constants.SSH_USER, constants.SSH_PASSWORD)
        ssh_handler.connect()
        content = ssh_handler.read_file_content_via_sftp(constants.ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG)

        # parse to object
        configuration = ConfigurationHelper.from_yaml_configuration(content.decode("utf-8"))

        # set to value of config
        configuration['permit_join'] = self.configuration['permit_join']

        new_configuration = ConfigurationHelper.to_yaml_configuration(configuration)
        # upload to host
        ssh_handler.write_file_content_via_sftp(constants.ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG, new_configuration)

        ssh_handler.disconnect()

        return 'Successfully fixed issue: ' + SecurityIssueTypes.ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME
