import string

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from handler.ssh.SshHandler import SshHandler


class IpIssueSolver:
    def __init__(self, configuration):
        self.configuration = configuration

    def fix_too_many_open_ports(self, ip: string):
        nmap_handler = NmapHandler()
        ssh_information = nmap_handler.get_ssh_information_by_ip(ip)

        # get from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)
        host_information = nmap_handler.get_host(nmap_report_db['nmaprun'], ip)

        if host_information is None:
            return 'Host not found!'

        ssh_handler = SshHandler(ssh_information.ip, ssh_information.port,
                                 constants.SSH_USER, constants.SSH_PASSWORD)
        ssh_handler.connect()

        skip_ports = self.configuration['whitelist_port']
        skip_ports.append(str(ssh_information.port))
        killed_ports = []
        for port in host_information.ports:
            if (port['@protocol'] == 'tcp') and (not port['@portid'] in skip_ports):
                output = ssh_handler.execute_command('sudo fuser -k ' + str(port['@portid']) + '/tcp')
                if output:
                    killed_ports.append(output[0].split('/')[0])

        ssh_handler.disconnect()

        if killed_ports:
            return 'Killed ports ' + str(killed_ports) + ' on host ' + str(ip) + '!'
        else:
            return 'No ports killed!'
