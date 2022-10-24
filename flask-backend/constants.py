FILE_OUTPUT_DIRECTORY = './output/'

ZIGBEE2MQTT_FILE_NAME = 'zigbee2mqtt_network_state.json'
ZIGBEE2MQTT_REMOTE_FILE_PATH = '/home/pi/IoT-Stack/data/zigbee2mqtt/state.json'

OSQUERY_DAEMON_LOCAL_OUTPUT_LOG_FILE_NAME = 'osquery_daemon_output.log'
OSQUERY_REMOTE_LOG_FILE_PATH = '/home/pi/osquery/logs/osqueryd.results.log'  # check permission of file; needs to be user 'pi'

NMAP_XML_REPORT_FILE_NAME = 'nmap_xml_result.xml'
NMAP_STANDARD_COMMAND_PREFIX = 'sudo nmap -oX - '  # space char at the end required
NMAP_COMMAND_FULL_SCAN_SUFFIX = '-sS -T4 -F 192.168.178.* --traceroute'

SSH_HOSTNAME = '192.168.178.51'  # todo dynamic ...?
SSH_PORT = '22'
SSH_USER = 'pi'
SSH_PASSWORD = 'raspberry'

PROCESS_NAME_SPLIT_CHAR = '>'
PROCESS_ENDLESS_NETWORK_SCAN_NAME = 'endless_network_scan'
PROCESS_ENDLESS_OSQUERY_SCAN_NAME = 'endless_osquery_scan'
PROCESS_ENDLESS_ZIGBEE2MQTT_STATE_NAME = 'endless_zigbee2mqtt_state'
PROCESS_LIST = [PROCESS_ENDLESS_NETWORK_SCAN_NAME, PROCESS_ENDLESS_OSQUERY_SCAN_NAME,
                PROCESS_ENDLESS_ZIGBEE2MQTT_STATE_NAME]

# collection names
OSQUERY_AND_COLLECTION_NAME_LISTENING_PORTS = 'listening_ports'
OSQUERY_AND_COLLECTION_NAME_PROCESSES = 'processes'
COLLECTION_NAME_NMAPRUN = 'nmaprun'
COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE = 'zigbee2mqtt_network_state'

MONGO_URI = 'mongodb://root:root@localhost:27017/pidb?authSource=admin'
PI_DATABASE_NAME = 'pidb'
