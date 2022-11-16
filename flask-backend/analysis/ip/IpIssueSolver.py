import string

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from handler.ssh.SshHandler import SshHandler


# Class responsible for solving ip security issues.
class IpIssueSolver:
    def __init__(self, configuration):
        self.configuration = configuration

    # Fix implementation if too many ports are open a given host.
    def fix_too_many_open_ports(self, ip: string):
        # get ssh information of last nmap scan from database
        nmap_handler = NmapHandler()
        ssh_information = nmap_handler.get_ssh_information_by_ip(ip)

        # get latest nmap scan from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)
        host_information = nmap_handler.get_host(nmap_report_db['nmaprun'], ip)

        if host_information is None:
            return 'Host not found!'

        # connect to host with ssh
        ssh_handler = SshHandler(ssh_information.ip, ssh_information.port,
                                 constants.SSH_USER, constants.SSH_PASSWORD)
        ssh_handler.connect()

        # read allow/listed ports
        allow_list_ports = self.configuration['allow_list_port']
        allow_list_ports = allow_list_ports.split('\n')
        # remove useless spaces
        allow_list_ports = [port.strip() for port in allow_list_ports]

        # add current ssh port otherwise connection will be cut off
        allow_list_ports.append(str(ssh_information.port))

        # kill all ports/application which are not in the allow-list
        killed_ports = []
        for port in host_information.ports:
            if (port['@protocol'] == 'tcp') and (not port['@portid'] in allow_list_ports):
                output = ssh_handler.execute_command('sudo fuser -k ' + str(port['@portid']) + '/tcp')
                if output:
                    killed_ports.append(output[0].split('/')[0])

        ssh_handler.disconnect()

        # return status
        if killed_ports:
            return 'Killed ports ' + str(killed_ports) + ' on host ' + str(ip) + '!'
        else:
            return 'No ports killed!'
