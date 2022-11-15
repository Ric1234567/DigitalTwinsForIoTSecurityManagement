import constants
from analysis.ip.IpAnalyser import IpAnalyser
from analysis.mosquitto.MosquittoAnalyser import MosquittoAnalyser
from analysis.osquery.OsqueryAnalyser import OsqueryAnalyser
from handler.DatabaseHandler import DatabaseHandler
from analysis.zigbee2Mqtt.Zigbee2MqttAnalyser import Zigbee2MqttAnalyser
from handler.HostInformation import HostInformation


# Provides the security analysis of a single host and implements methods to use the Zigbee2MqttAnalyser,
# MosquittoAnalyser, OsqueryAnalyser and IpAnalyser.
class HostAnalyser:

    def __init__(self, should_configuration, host_information: HostInformation):
        self.configuration = should_configuration
        self.host_information: HostInformation = host_information
        self.database_handler = DatabaseHandler(constants.MONGO_URI)

    # Responsible for the security analysis.
    # Implements Zigbee2MqttAnalyser, MosquittoAnalyser, OsqueryAnalyser and IpAnalyser.
    def analyse(self):
        security_issues = []

        # check if ssh available. (needed to get configuration and log data)
        if self.host_information.ssh_information is not None:
            zigbee2mqtt_issues = self.analyse_zigbee2mqtt()
            if zigbee2mqtt_issues is not None:
                security_issues.append(zigbee2mqtt_issues)

            mosquitto_issues = self.analyse_mosquitto()
            if mosquitto_issues is not None:
                security_issues.append(mosquitto_issues)

            osquery_issues = self.analyse_osquery_information()
            if osquery_issues is not None:
                security_issues.append(osquery_issues)

        # ip issues can be analysed without ssh.
        ip_issues = self.ip_analysis()
        if ip_issues is not None:
            security_issues.append(ip_issues)

        return security_issues

    # Host analysis of the Zigbee2Mqtt Integration
    def analyse_zigbee2mqtt(self):
        print('Analysis zigbee2Mqtt')

        # get configuration from database
        entry = self.database_handler.get_latest_zigbee2mqtt_entry_of_host(self.host_information.ip)

        # filter host to analyse
        host_scan = None
        for scan in entry['scans']:
            if scan['host'] == self.host_information.ip:
                host_scan = scan

        # start analysis
        zigbee2mqtt_analyser = Zigbee2MqttAnalyser(self.configuration['zigbee_2_mqtt'])
        security_issue_permit_join = zigbee2mqtt_analyser.compare_permit_join_flag(self.host_information, host_scan)

        return security_issue_permit_join

    # Host analysis of the Mosquitto Integration
    def analyse_mosquitto(self):
        print('Analysis Mosquitto')

        # get acl from database
        entry = self.database_handler.get_latest_mosquitto_entry_of_host(self.host_information.ip)

        # start analysis
        mosquitto_analyser = MosquittoAnalyser(self.configuration['mosquitto'])
        security_issue_acl = mosquitto_analyser.compare_access_control_list(self.host_information, entry)

        return security_issue_acl

    # Host analysis of the osquery Integration
    def analyse_osquery_information(self):
        print('Analysis Osquery')

        # start analysis
        osquery_analyser = OsqueryAnalyser(self.configuration['osquery'])
        security_issue_usbs = osquery_analyser.check_connected_usb_devices(self.host_information)

        return security_issue_usbs

    # Host analysis of the ip Integration
    def ip_analysis(self):
        print('Analysis IP')

        # start analysis
        ip_analyser = IpAnalyser(self.configuration['ip_configuration'])
        security_issue_ip = ip_analyser.check_open_ports(self.host_information)

        return security_issue_ip
