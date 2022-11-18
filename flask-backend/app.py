import json
import string
from multiprocessing import active_children

from flask import Flask, Response, request
from flask_cors import CORS
from flask_pymongo import PyMongo

from analysis.host.HostSolver import HostSolver
from services import ServiceConstants
from services.FullScanService import FullScanService
from services.MosquittoScanService import MosquittoScanService
from services.NmapScanService import NmapScanService
from services.OsqueryScanService import OsqueryScanService
from services.Zigbee2MqttScanService import Zigbee2MqttScanService
from util import ConfigurationHelper
from util.ComplexJsonEncoder import ComplexJsonEncoder
from analysis.host.HostAnalyser import HostAnalyser
from handler.SubnetworkHandler import SubnetworkHandler
import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config["MONGO_URI"] = constants.MONGO_URI  # pi database
mongo = PyMongo(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

database_handler = DatabaseHandler(constants.MONGO_URI)
running_services = []


@app.route('/custom_network_scan/<nmap_command>', methods=['GET'])
def get_custom_nmap_report(nmap_command: string):
    try:
        nmap_handler = NmapHandler()
        nmap_handler.custom_network_scan(nmap_command)

        # get from database
        nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        response_json = {
            "response": {
                'nmap_unixTime': nmap_report_db['unixTime'],
                'nmaprun': nmap_report_db['nmaprun']
            }}
        return Response(json.dumps(response_json), status=200, mimetype='application/json')
    except FileNotFoundError as e:
        return Response(str(e), status=404, mimetype='application/json')


@app.route('/full_network_scan/<nmap_command>', methods=['GET'])
def get_full_network_report(nmap_command: string):
    nmap_handler = NmapHandler()
    nmap_handler.custom_network_scan(nmap_command)

    # get from database
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

    subnetwork_handler = SubnetworkHandler()

    for host in ssh_hosts:
        subnetwork_handler.scan_subnetwork_host(host)
    subnetwork, unix_time = subnetwork_handler.get_latest_subnetwork_information()

    response_json = {
        "response": {
            'nmap_unixTime': nmap_report_db['unixTime'],
            'nmaprun': nmap_report_db['nmaprun'],
            'subnetwork_unixTime': unix_time,
            'subnetwork': subnetwork
        }}
    return Response(json.dumps(response_json), status=200, mimetype='application/json')


@app.route('/last_network_scan', methods=['GET'])
def get_last_network_report():
    try:
        nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        subnetwork_handler = SubnetworkHandler()
        subnetwork, unix_time = subnetwork_handler.get_latest_subnetwork_information()

        response_json = {
            "response": {
                'nmap_unixTime': nmap_report_db['unixTime'],
                'nmaprun': nmap_report_db['nmaprun'],
                'subnetwork_unixTime': unix_time,
                'subnetwork': subnetwork
            }}
        return Response(json.dumps(response_json), status=200, mimetype='application/json')
    except FileNotFoundError as e:
        return Response(str(e), status=404, mimetype='application/json')


@app.route('/stop/<process_pid>', methods=['GET'])
def stop_service(process_pid):
    try:
        for service in running_services:
            if service.process.pid == int(process_pid):
                service.stop()
                running_services.remove(service)
                print("terminated process " + service.name + ", pid=" + str(service.process.pid))

                response_json = {"response": 'Success! Stopped process ' + service.name}
                return Response(json.dumps(response_json), status=200, mimetype='application/json')

    except Exception as e:
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/start/<process_name>', methods=['GET'])
def start_service(process_name):
    try:
        nmap_command = request.args.get('cmd')
        ip_address = request.args.get('ip')
        ssh_port = request.args.get('ssh_port')
        delay = request.args.get('delay')

        if (process_name == ServiceConstants.PROCESS_ENDLESS_NMAP_SCAN_NAME) or \
                (process_name == ServiceConstants.PROCESS_ENDLESS_FULL_NETWORK_SCAN_NAME):

            if (not nmap_command) or (not delay):
                raise Exception('Missing parameter! Given: cmd=' + str(nmap_command) + ', delay=' + str(delay))

            if process_name == ServiceConstants.PROCESS_ENDLESS_NMAP_SCAN_NAME:
                service = NmapScanService(process_name,
                                          'Nmap-Scan with args: cmd=' +
                                          str(nmap_command) + ', delay=' + str(delay),
                                          (nmap_command, int(delay),))
            else:  # full scan
                service = FullScanService(process_name,
                                          'Full-Scan with args: cmd=' +
                                          str(nmap_command) + ', delay=' + str(delay),
                                          (nmap_command, int(delay),))
        elif process_name == ServiceConstants.PROCESS_ENDLESS_OSQUERY_SCAN_NAME:
            if (not ip_address) or (not ssh_port) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) +
                                ', ssh_port=' + str(ssh_port) + ', delay=' + str(delay))

            service = OsqueryScanService(process_name,
                                         'Osquery-Scan with args: ip=' +
                                         str(ip_address) + ', ssh_port=' + ssh_port + ', delay=' + str(delay),
                                         (ip_address, int(ssh_port), int(delay),))

        elif process_name == ServiceConstants.PROCESS_ENDLESS_ZIGBEE2MQTT_STATE_NAME:
            if (not delay) or (not ip_address) or (not ssh_port):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) +
                                ', ssh_port=' + str(ssh_port) + ', delay=' + str(delay))

            service = Zigbee2MqttScanService(process_name,
                                             'Zigbee2Mqtt-Scan with args: ip=' +
                                             str(ip_address) + ', ssh_port=' + ssh_port + ', delay=' + str(
                                                 delay),
                                             (ip_address, int(ssh_port), int(delay),))

        elif process_name == ServiceConstants.PROCESS_ENDLESS_MOSQUITTO_SCAN_NAME:
            if (not ip_address) or (not ssh_port) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) + ', ssh_port=' + str(ssh_port) +
                                ', delay=' + str(delay))

            service = MosquittoScanService(process_name,
                                           'Mosquitto-Scan with args: ip=' +
                                           str(ip_address) + ', ssh_port=' + ssh_port + ', delay=' + str(
                                               delay),
                                           (ip_address, int(ssh_port), int(delay),))

        else:
            response_json = {"response": 'Process not found!'}
            return Response(json.dumps(response_json), status=500, mimetype='application/json')

        # start service
        service.start()
        running_services.append(service)

        # convert to json
        service_json = json.dumps(service, cls=ComplexJsonEncoder)

        response_json = {"response": 'Success! Started process ' + service_json}
        return Response(json.dumps(response_json), status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/available_services', methods=['GET'])
def get_available_services():
    response = {"response": ServiceConstants.SERVICE_LIST}
    return Response(json.dumps(response), status=200, mimetype='application/json')


@app.route('/running_services', methods=['GET'])
def get_running_services():
    response = {"response": running_services}
    return Response(json.dumps(response, cls=ComplexJsonEncoder), status=200, mimetype='application/json')


@app.route('/network_configuration', methods=['GET', 'POST'])
def get_configuration():
    if request.method == 'GET':
        with open(constants.NETWORK_CONFIGURATION_FILE_NAME, 'r') as file:
            configuration_json = file.read()

        return Response(configuration_json, status=200, mimetype='application/json')
    elif request.method == 'POST':
        with open(constants.NETWORK_CONFIGURATION_FILE_NAME, 'w') as file:
            file.write(request.data.decode('utf-8'))

        response = {"response": "Successfully submitted network configuration!"}
        return Response(json.dumps(response), status=200, mimetype='application/json')
    else:
        response = {"response": request.data.decode('utf-8')}
        return Response(json.dumps(response), status=405, mimetype='application/json')


@app.route('/analysis/<host_ip>', methods=['GET'])
def execute_analysis(host_ip):
    print('Starting analysis for host ' + host_ip)

    should_configuration = ConfigurationHelper.read_network_configuration()

    nmap_handler = NmapHandler()
    nmap_handler.custom_network_scan("-sS -T4 -p1-65535 " + host_ip)

    # get from database
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    hosts = nmap_handler.get_hosts_including_ssh_information(nmap_report_db['nmaprun'])

    # identify correct host by host todo refactor
    host_to_analyse = None
    for host in hosts:
        if host.ip == host_ip:
            host_to_analyse = host
            break

    if host_to_analyse is None:
        response = {"response": "Could not find host!"}
        return Response(json.dumps(response), status=500, mimetype='application/json')

    host_analyser = HostAnalyser(should_configuration, host_to_analyse)
    host_analysis_result = host_analyser.analyse()

    # convert to json
    host_analysis_result_json = json.dumps(host_analysis_result, cls=ComplexJsonEncoder)

    print("Write host analysis of " + host_to_analyse.ip + " to database")
    database_handler.insert_one_into(constants.COLLECTION_NAME_HOST_ANALYSIS, json.loads(host_analysis_result_json))

    if len(host_analysis_result.security_issues) == 0:
        response = {"response": "No issues found!"}
        return Response(json.dumps(response), status=200, mimetype='application/json')

    return Response(host_analysis_result_json, status=200, mimetype='application/json')


@app.route('/fix/<host_ip>/<issue_type>', methods=['GET'])
def execute_fix(host_ip, issue_type):
    print('Fix ' + host_ip + ' ' + issue_type)

    should_configuration = ConfigurationHelper.read_network_configuration()

    host_solver = HostSolver(should_configuration)
    result = host_solver.solve(host_ip, issue_type)

    response = {"response": result}
    return Response(json.dumps(response), status=200, mimetype='application/json')


@app.route('/ip_hosts', methods=['GET'])
def get_ip_hosts():
    print('Get hosts of last nmaprun...')

    nmap_handler = NmapHandler()
    nmap_handler.custom_network_scan("-sn -T4 " + constants.IP_NETWORK_PREFIX + "*")

    # get from database
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    hosts = nmap_handler.get_hosts_including_ssh_information(nmap_report_db['nmaprun'])

    return Response(json.dumps([ssh_host.__dict__ for ssh_host in hosts], cls=ComplexJsonEncoder),
                    status=200,
                    mimetype='application/json')


if __name__ == '__main__':
    app.run(use_reloader=False)

    # wait for running_services to complete
    for process in active_children():
        process.join()
