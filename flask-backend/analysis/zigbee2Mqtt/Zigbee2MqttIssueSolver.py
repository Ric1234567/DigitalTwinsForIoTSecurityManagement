import string

from util import ConfigurationHelper
import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from analysis import SecurityIssueTypes, DockerConstants
from handler.ssh.SshHandler import SshHandler


class Zigbee2MqttIssueSolver:
    def __init__(self, configuration):
        self.configuration = configuration

    def fix_permit_join(self, ip: string):
        # get from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        # get ssh information of the host
        nmap_handler = NmapHandler()
        ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])
        ssh_information = None
        for ssh_host in ssh_hosts:
            if ssh_host.ip == ip:
                ssh_information = ssh_host
                break

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

        # restart zigbee2mqtt
        print('Restarting zigbee2mqtt docker container on host ' + ip)
        ssh_handler.execute_command('sudo docker restart ' + DockerConstants.ZIGBEE2MQTT_CONTAINER_NAME)

        ssh_handler.disconnect()

        return 'Successfully fixed issue: ' + SecurityIssueTypes.ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME

