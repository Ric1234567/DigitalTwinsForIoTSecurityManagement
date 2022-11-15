import string

from util import ConfigurationHelper
import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from analysis import SecurityIssueTypes, DockerConstants
from handler.ssh.SshHandler import SshHandler


# Solver class for Zigbee2Mqtt security issues. (ssh to fix required)
class Zigbee2MqttIssueSolver:
    def __init__(self, configuration):
        self.configuration = configuration

    # change the permit join flag in the devices configuration
    def fix_permit_join(self, ip: string):
        # get ssh information of last nmap scan from database
        nmap_handler = NmapHandler()
        ssh_information = nmap_handler.get_ssh_information_by_ip(ip)

        # connect to host with ssh
        ssh_handler = SshHandler(ssh_information.ip, ssh_information.port,
                                 constants.SSH_USER, constants.SSH_PASSWORD)
        ssh_handler.connect()
        # get configuration content from host
        content = ssh_handler.read_file_content_via_sftp(constants.ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG)

        # parse to configuration to readable object
        configuration = ConfigurationHelper.from_yaml_configuration(content.decode("utf-8"))

        # set to value of config
        configuration['permit_join'] = self.configuration['permit_join']

        # convert to yaml string configuration
        new_configuration = ConfigurationHelper.to_yaml_configuration(configuration)

        # upload to host
        ssh_handler.write_file_content_via_sftp(constants.ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG, new_configuration)

        # restart zigbee2mqtt to apply
        print('Restarting zigbee2mqtt docker container on host ' + ip)
        ssh_handler.execute_command('sudo docker restart ' + DockerConstants.ZIGBEE2MQTT_CONTAINER_NAME)

        ssh_handler.disconnect()

        return 'Successfully fixed issue: ' + SecurityIssueTypes.ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME

