import collections.abc
import json
import string
import subprocess
import time
import typing
from multiprocessing import current_process

from libnmap.parser import NmapParser

import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.HostInformation import HostInformation
from handler.ssh.SshInformation import SshInformation
from util import ConfigurationHelper


# Class responsible for nmap related operations
class NmapHandler:
    def __init__(self):
        self.database_handler = DatabaseHandler(constants.MONGO_URI)

    # Runs nmap commands and return xml string
    def run_command(self, cmd):
        process = subprocess.run(cmd, shell=True, check=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout

    # parse an nmap xml string to a python object
    def parse_xml_result(self, xml_result):
        return NmapParser.parse_fromstring(xml_result)

    # execute a nmap network scan with the given command_suffix.
    # The prefix needs to be constant to operate as sudo, and to return an xml result.
    def scan_network(self, command_suffix):
        nmap_xml_result = self.run_command(constants.NMAP_STANDARD_COMMAND_PREFIX + command_suffix)
        self.save_report(nmap_xml_result)
        return nmap_xml_result

    # wrapper method for scanning and parsing of nmap scan
    def get_report(self, command_suffix):
        nmap_xml_result = self.scan_network(command_suffix)
        return self.parse_xml_result(nmap_xml_result)

    # execute an nmap command and return the result as json string
    def get_report_as_json(self, command_suffix):
        nmap_xml_result = self.scan_network(command_suffix)
        return ConfigurationHelper.convert_xml_to_json(nmap_xml_result)

    # save report to the output file dir
    def save_report(self, nmap_xml_result):
        with open(constants.FILE_OUTPUT_DIRECTORY + constants.NMAP_XML_REPORT_FILE_NAME, 'w') as file:
            file.write(nmap_xml_result)

    # read report from the output file dir
    def load_report(self):
        with open(constants.FILE_OUTPUT_DIRECTORY + constants.NMAP_XML_REPORT_FILE_NAME, 'r') as file:
            return file.read()

    # wrapper method to read in report from the output dir as json
    def load_report_as_json(self):
        report = self.load_report()
        return ConfigurationHelper.convert_xml_to_json(report)

    # perform a custom network scan command which result gets written to the database
    def custom_network_scan(self, nmap_command: string):
        nmap_report_json = self.get_report_as_json(nmap_command)

        # save to database
        self.insert_nmaprun_to_database(nmap_report_json)

    # get hosts of network with its ssh information if any
    def get_hosts_including_ssh_information(self, nmaprun):
        # perform ssh discovery
        ssh_informations = self.ssh_service_discovery(nmaprun)
        ip_hosts = self.get_hosts(nmaprun)

        # relate ssh host data to ip host data
        for host in ip_hosts:
            for ssh_information in ssh_informations:
                if host.ip == ssh_information.ip:
                    host.ssh_information = ssh_information
        return ip_hosts

    # find ssh services running in an given nmap scan
    def ssh_service_discovery(self, nmaprun):
        ssh_hosts: typing.List[SshInformation] = []
        if 'host' in nmaprun:
            if not isinstance(nmaprun['host'], collections.abc.Sequence):  # convert to array if none
                nmaprun['host'] = [nmaprun['host']]
            for host in nmaprun['host']:
                ssh_port = None

                if 'ports' in host:
                    if 'port' in host['ports']:
                        if not isinstance(host['ports']['port'], collections.abc.Sequence):  # convert to array if none
                            host['ports']['port'] = [host['ports']['port']]

                        # search ports for services with the name ssh
                        for port in host['ports']['port']:
                            if 'service' in port:
                                if '@name' in port['service']:
                                    if port['service']['@name'] == 'ssh':
                                        ssh_port = port['@portid']
                                        break

                if ssh_port is None:
                    continue  # no ssh service on this host

                ssh_ip = self.get_ipv4_address(host)

                # ip and port needs to be set
                if (ssh_ip is not None) and (ssh_port is not None):
                    ssh_information_host = SshInformation(ssh_ip, ssh_port)
                    ssh_hosts.append(ssh_information_host)

        return ssh_hosts

    # get a list of all hosts in an given nmap network scan
    def get_hosts(self, nmaprun):
        hosts = []
        if 'host' in nmaprun:
            for host in nmaprun['host']:
                ip = self.get_ipv4_address(host)
                hostname = host['hostnames']['hostname']['@name']
                ports = None

                if 'ports' in host:
                    if 'port' in host['ports']:
                        if not isinstance(host['ports']['port'], collections.abc.Sequence):  # convert to array if none
                            ports = [host['ports']['port']]
                        else:
                            ports = host['ports']['port']
                        
                host_information = HostInformation(ip, hostname, ports)
                hosts.append(host_information)

        return hosts

    # get a single host in an given nmap network scan by ip
    def get_host(self, nmaprun, search_ip: string):
        if 'host' in nmaprun:
            if not isinstance(nmaprun['host'], collections.abc.Sequence):
                nmaprun['host'] = [nmaprun['host']]
            for host in nmaprun['host']:
                ipv4 = self.get_ipv4_address(host)
                if ipv4 == search_ip:
                    hostname = host['hostnames']['hostname']['@name']
                    ports = None

                    if 'ports' in host:
                        if 'port' in host['ports']:
                            if not isinstance(host['ports']['port'], collections.abc.Sequence):
                                ports = [host['ports']['port']]
                            else:
                                ports = host['ports']['port']

                    host_information = HostInformation(ipv4, hostname, ports)
                    return host_information

        return None

    # get the ipv4 address of an nmaprun host
    def get_ipv4_address(self, host):
        if 'address' in host:
            if not isinstance(host['address'], collections.abc.Sequence):
                host['address'] = [host['address']]
            for address in host['address']:
                if address['@addrtype'] == 'ipv4':
                    return address['@addr']
        return None

    # get ssh information of a host by a given ip from database
    def get_ssh_information_by_ip(self, ip: string):
        # get from database
        nmap_report_db = self.database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        # get ssh information of the host
        nmap_handler = NmapHandler()
        ssh_information_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])
        ssh_information = None
        for ssh_information_host in ssh_information_hosts:
            if ssh_information_host.ip == ip:  # identify host by ip
                ssh_information = ssh_information_host
                break

        return ssh_information

    # write an nmaprun json to the database. add an unix timestamp to the data
    def insert_nmaprun_to_database(self, nmap_report_json: string):
        print("Writing result of nmap scan to database (" + current_process().name + ")")
        try:
            test = '{"unixTime":' + str(round(time.time())) + ',' + nmap_report_json[1:-1] + '}'
            nmap_report = json.loads(test)
            self.database_handler.insert_one_into(constants.COLLECTION_NAME_NMAPRUN, nmap_report)
        except Exception as e:
            print(e)
            return
