import string

import constants
from analysis import SecurityIssueTypes, DockerConstants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from handler.ssh.SshHandler import SshHandler


class MosquittoIssueSolver:
    def __init__(self, configuration):
        self.configuration = configuration

    def fix_access_control_list(self, ip: string):
        # get from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        # get ssh information of the host
        nmap_handler = NmapHandler()
        ssh_information_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])
        ssh_information = None
        for ssh_information_host in ssh_information_hosts:
            if ssh_information_host.ip == ip:
                ssh_information = ssh_information_host
                break

        # replace acl list on host with the config
        ssh_handler = SshHandler(ssh_information.ip, ssh_information.port,
                                 constants.SSH_USER, constants.SSH_PASSWORD)
        ssh_handler.connect()
        ssh_handler.write_file_content_via_sftp(constants.MOSQUITTO_REMOTE_CONFIG_DIR_PATH +
                                                constants.MOSQUITTO_REMOTE_ACL_FILE_NAME,
                                                self.configuration['acl'])

        print('Restarting mosquitto and zigbee2mqtt docker container...')
        ssh_handler.execute_command('sudo docker restart ' + DockerConstants.MOSQUITTO_CONTAINER_NAME)
        ssh_handler.execute_command('sudo docker restart ' + DockerConstants.ZIGBEE2MQTT_CONTAINER_NAME)

        ssh_handler.disconnect()

        return 'Successfully fixed issue: ' + SecurityIssueTypes.MOSQUITTO_ACCESS_CONTROL_LIST
