import constants
from DatabaseHandler import DatabaseHandler
from Recommendation import Recommendation


class HostAnalyser:

    def __init__(self, should_configuration, ip):
        self.configuration = should_configuration
        self.ip = ip

    def analyse_zigbee2mqtt(self):
        print('Analysis Zigbee2Mqtt')
        database_handler = DatabaseHandler(constants.MONGO_URI)
        entry = database_handler.get_latest_zigbee2mqtt_entry_of_host(self.ip)
        host_scan = None
        for scan in entry['scans']:
            if scan['host'] == self.ip:
                host_scan = scan

        # todo problem definition with id and method to fix it.....
        # start analysis
        if host_scan['config']['permit_join'] is not self.configuration['zigbee_2_mqtt']['permit_join']:
            return Recommendation(constants.ZIGBEE2MQTT, 'The permit_join flag in host ' + self.ip +
                                  ' is not equal to the definition in the should_configuration. ' +
                                  '(host permit_join=' + str(host_scan['config']['permit_join']) +
                                  ', should_configuration permit_join=' +
                                  str(self.configuration['zigbee_2_mqtt']['permit_join']) + ')')
        else:
            return None

    def analyse_mosquitto(self):
        # todo topic access etc
        print()

    def analyse_osquery_information(self):
        print()
        # todo usb and ports