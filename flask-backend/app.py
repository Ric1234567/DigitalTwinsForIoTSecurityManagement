from flask import Flask, Response
from flask_cors import CORS
import SshHandler
import constants
import jsonHandler
from NmapHandler import NmapHandler
import sqlite3

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/custom_network_scan/<nmap_command>', methods=['GET'])
def get_custom_network_report(nmap_command):
    try:
        nmap_handler = NmapHandler()
        return nmap_handler.get_report_as_json(nmap_command)
    except FileNotFoundError as e:
        return Response(str(e), status=404, mimetype='application/json')


@app.route('/network_scan', methods=['GET'])
def get_network_report():
    try:
        nmap_handler = NmapHandler()
        return nmap_handler.get_report_as_json(constants.NMAP_COMMAND_FULL_SCAN_PREFIX)
    except FileNotFoundError as e:
        return Response(str(e), status=404, mimetype='application/json')


@app.route('/last_network_scan', methods=['GET'])
def get_old_network_report():
    try:
        nmap_handler = NmapHandler()
        return nmap_handler.load_report_as_json()
    except FileNotFoundError as e:
        return Response(str(e), status=404, mimetype='application/json')


@app.route('/daemon', methods=['GET'])
def get_daemon_output():
    ssh_handler = SshHandler.SshHandler(constants.SSH_HOSTNAME, constants.SSH_PORT, constants.SSH_USER,
                                        constants.SSH_PASSWORD)
    ssh_handler.connect()

    file_name = 'daemon_output.log'
    remote_path = '/home/pi/osquery/logs/osqueryd.results.log'  # check permission of file; needs to be user 'pi'

    ssh_handler.get_file_via_sftp(constants.FILE_OUTPUT_DIRECTORY + file_name, remote_path)
    ssh_handler.disconnect()

    with open(constants.FILE_OUTPUT_DIRECTORY + file_name, 'r') as file:
        data = file.read()
    return data  # not a json


@app.route('/processes', methods=['GET'])
def get_processes():
    json_data = get_daemon_output()
    return jsonHandler.filter_json_array(json_data.split('\n'), 'name', 'processes')


@app.route('/listening_ports', methods=['GET'])
def get_listening_ports():
    json_data = get_daemon_output()
    return jsonHandler.filter_json_array(json_data.split('\n'), 'name', 'listening_ports')


if __name__ == '__main__':
    app.run()
