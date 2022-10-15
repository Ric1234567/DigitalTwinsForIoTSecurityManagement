import subprocess
from libnmap.parser import NmapParser

import constants


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
    #NmapParser.parse_fromfile()

    def get_report(self):
        # nmap_xml_result = self.run_command("nmap -oX - -sT -T4 192.168.178.51")
        nmap_xml_result = self.run_command("sudo nmap -oX - -sS -T4 -F 192.168.178.* --traceroute")

        file_name = 'nmap_xml_result.xml'
        self.save_report(nmap_xml_result, file_name)

        return self.parse_xml_result(nmap_xml_result)

    def save_report(self, nmap_xml_result, file_name):
        with open(constants.FILE_OUTPUT_DIRECTORY + file_name, 'w') as file:
            file.write(nmap_xml_result)