import collections.abc
import string
import subprocess
from multiprocessing import current_process

from libnmap.parser import NmapParser
import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.ssh.SshInformation import SshInformation


class NmapHandler:
    # cmd = "sudo nmap -oX test.txt -sS -T4 -F 192.168.178.* --traceroute"
    # cmdsimple = "nmap -oX - -sT -T4 192.168.178.51"

    def run_command(self, cmd):
        """
        Runs nmap commands and return xml string
        """
        # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process = subprocess.run(cmd, shell=True, check=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout

    def parse_xml_result(self, xml_result):
        return NmapParser.parse_fromstring(xml_result)

    def scan_network(self, command_suffix):
        nmap_xml_result = self.run_command(constants.NMAP_STANDARD_COMMAND_PREFIX + command_suffix)
        self.save_report(nmap_xml_result)
        return nmap_xml_result

    def get_report(self, command_suffix):
        nmap_xml_result = self.scan_network(command_suffix)
        return self.parse_xml_result(nmap_xml_result)

    def get_report_as_json(self, command_suffix):
        nmap_xml_result = self.scan_network(command_suffix)
        return JsonHandler.convert_xml_to_json(nmap_xml_result)

    def save_report(self, nmap_xml_result):
        with open(constants.FILE_OUTPUT_DIRECTORY + constants.NMAP_XML_REPORT_FILE_NAME, 'w') as file:
            file.write(nmap_xml_result)

    def load_report(self):
        with open(constants.FILE_OUTPUT_DIRECTORY + constants.NMAP_XML_REPORT_FILE_NAME, 'r') as file:
            return file.read()

    def load_report_as_json(self):
        report = self.load_report()
        return JsonHandler.convert_xml_to_json(report)

    def custom_network_scan(self, nmap_command: string):
        nmap_report_json = self.get_report_as_json(nmap_command)

        # save to database
        print("Writing result of nmap scan to database (" + current_process().name + ")")
        database_handler = DatabaseHandler(constants.MONGO_URI)
        database_handler.write_nmaprun_to_database(nmap_report_json)

    def ssh_service_discovery(self, nmaprun):
        ssh_hosts = []
        if 'host' in nmaprun:
            if not isinstance(nmaprun['host'], collections.abc.Sequence):  # convert to array if none
                nmaprun['host'] = [nmaprun['host']]
            for host in nmaprun['host']:
                if 'ports' in host:
                    if 'port' in host['ports']:
                        if not isinstance(host['ports']['port'], collections.abc.Sequence):
                            host['ports']['port'] = [host['ports']['port']]
                        for port in host['ports']['port']:
                            if 'service' in port:
                                if '@name' in port['service']:
                                    if port['service']['@name'] == 'ssh':
                                        ssh_hosts.append({'host_address': host['address'],
                                                          'port': port})
        return ssh_hosts

    def get_ssh_information(self, ssh_host):
        for address in ssh_host['host_address']:
            if address['@addrtype'] == 'ipv4':
                ipv4_address = address['@addr']
                port = ssh_host['port']['@portid']

                return SshInformation(ipv4_address, port)
