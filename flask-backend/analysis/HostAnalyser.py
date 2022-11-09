import constants
from analysis.mosquitto.MosquittoAnalyser import MosquittoAnalyser
from handler.DatabaseHandler import DatabaseHandler
from analysis.zigbee2Mqtt.Zigbee2MqttAnalyser import Zigbee2MqttAnalyser


class HostAnalyser:

    def __init__(self, should_configuration, ip):
        self.configuration = should_configuration
        self.ip = ip
        self.database_handler = DatabaseHandler(constants.MONGO_URI)

    def analyse(self):
        security_issues = []

        zigbee2mqtt_issues = self.analyse_zigbee2mqtt()
        if zigbee2mqtt_issues is not None:
            security_issues.append(zigbee2mqtt_issues)

        mosquitto_issues = self.analyse_mosquitto()
        if mosquitto_issues is not None:
            security_issues.append(mosquitto_issues)

        # todo here other analysis

        return security_issues

    def analyse_zigbee2mqtt(self):
        print('Analysis zigbee2Mqtt')

        # get from database
        entry = self.database_handler.get_latest_zigbee2mqtt_entry_of_host(self.ip)

        # filter host
        host_scan = None
        for scan in entry['scans']:
            if scan['host'] == self.ip:
                host_scan = scan

        # start analysis
        zigbee2mqtt_analyser = Zigbee2MqttAnalyser(self.configuration['zigbee_2_mqtt'])
        security_issue_permit_join = zigbee2mqtt_analyser.compare_permit_join_flag(self.ip, host_scan)

        return security_issue_permit_join

    def analyse_mosquitto(self):
        print('Analysis Mosquitto')

        # get from database

        entry = self.database_handler.get_latest_mosquitto_entry_of_host(self.ip)

        # start analysis
        mosquitto_analyser = MosquittoAnalyser(self.configuration['mosquitto'])
        security_issue_acl = mosquitto_analyser.compare_access_control_list(self.ip, entry)

        return security_issue_acl

    def analyse_osquery_information(self):
        print()
        # todo usb and ports
