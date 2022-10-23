FILE_OUTPUT_DIRECTORY = './output/'

NMAP_XML_REPORT_FILE_NAME = 'nmap_xml_result.xml'
NMAP_STANDARD_COMMAND_PREFIX = 'sudo nmap -oX - '  # space char at the end required
NMAP_COMMAND_FULL_SCAN_SUFFIX = '-sS -T4 -F 192.168.178.* --traceroute'


SSH_HOSTNAME = '192.168.178.51'
SSH_PORT = '22'
SSH_USER = 'pi'
SSH_PASSWORD = 'raspberry'


PROCESS_SPLIT_CHAR = '>'
PROCESS_ENDLESS_NETWORK_SCAN_NAME = 'endless_network_scan'
PROCESS_GET_DAEMON_DATA = 'get_daemon_data'

DAEMON_AND_COLLECTION_NAME_LISTENING_PORTS = 'listening_ports'
DAEMON_AND_COLLECTION_NAME_PROCESSES = 'processes'
COLLECTION_NAME_NMAPRUN = 'nmaprun'
