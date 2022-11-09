FILE_OUTPUT_DIRECTORY = './output/'

NETWORK_CONFIGURATION_FILE_NAME = 'configuration.json'

ZIGBEE2MQTT_FILE_NAME = 'zigbee2mqtt_network_state.json'
ZIGBEE2MQTT_FILE_NAME_CONFIG = 'zigbee2mqtt_config.json'
ZIGBEE2MQTT_REMOTE_FILE_PATH = '/home/pi/IoT-Stack/data/zigbee2mqtt/state.json'
ZIGBEE2MQTT_REMOTE_FILE_PATH_CONFIG = '/home/pi/IoT-Stack/data/zigbee2mqtt/configuration.yaml'

MOSQUITTO_REMOTE_CONFIG_FILE_NAME = 'mosquitto.conf'
MOSQUITTO_REMOTE_ACL_FILE_NAME = 'acl.acl'
MOSQUITTO_REMOTE_CONFIG_DIR_PATH = '/home/pi/IoT-Stack/data/mosquitto/config/'
MOSQUITTO_FILE_NAME_CONFIG = 'mosquitto.conf'
MOSQUITTO_FILE_NAME_ACL = 'mosquitto_acl.acl'

OSQUERY_DAEMON_LOCAL_OUTPUT_LOG_FILE_NAME = 'osquery_daemon_output.log'
OSQUERY_REMOTE_LOG_FILE_PATH = '/home/pi/osquery/logs/osqueryd.results.log'  # check permission of file; needs to be user 'pi'

NMAP_XML_REPORT_FILE_NAME = 'nmap_xml_result.xml'
NMAP_STANDARD_COMMAND_PREFIX = 'sudo nmap -oX - '  # space char at the end required
NMAP_COMMAND_FULL_SCAN_SUFFIX = '-sS -T4 -F 192.168.178.* --traceroute'

# SSH_HOSTNAME = '192.168.178.51'
# SSH_PORT = '22'
SSH_USER = 'pi'
SSH_PASSWORD = 'raspberry'


# collection names
OSQUERY_AND_COLLECTION_NAME_LISTENING_PORTS = 'listening_ports'
OSQUERY_AND_COLLECTION_NAME_PROCESSES = 'processes'
COLLECTION_NAME_NMAPRUN = 'nmaprun'
COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE = 'zigbee2mqtt_network_state'
COLLECTION_NAME_MOSQUITTO_CONFIG = 'mosquitto'

MONGO_URI = 'mongodb://root:root@localhost:27017/pidb?authSource=admin'
PI_DATABASE_NAME = 'pidb'

ZIGBEE2MQTT = 'zigbee2Mqtt'
MOSQUITTO = 'mosquitto'
