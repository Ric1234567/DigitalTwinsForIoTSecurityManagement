import json
import string

from flask import Flask, Response, request
from flask_cors import CORS
from flask_pymongo import PyMongo

from analysis.mosquitto.MosquittoIssueSolver import MosquittoIssueSolver
from services import NmapService, FullScanService, OsqueryService, Zigbee2MqttService, MosquittoService
from util import ConfigurationHelper
from util.ComplexJsonEncoder import ComplexJsonEncoder
from analysis import SecurityIssueTypes
from analysis.HostAnalyser import HostAnalyser
from handler import ServiceHandler
from handler.SubnetworkHandler import SubnetworkHandler
import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from analysis.zigbee2Mqtt.Zigbee2MqttIssueSolver import Zigbee2MqttIssueSolver

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config["MONGO_URI"] = constants.MONGO_URI  # pi database
mongo = PyMongo(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/custom_network_scan/<nmap_command>', methods=['GET'])
def get_custom_nmap_report(nmap_command: string):
    try:
        nmap_handler = NmapHandler()
        nmap_handler.custom_network_scan(nmap_command)

        # get from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

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
    database_handler = DatabaseHandler(constants.MONGO_URI)
    nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

    subnetwork_handler = SubnetworkHandler()
    subnetwork_handler.scan_subnetwork(ssh_hosts)
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
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

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
        p = ServiceHandler.process_dict.pop(int(process_pid))
        p.terminate()
        print("terminated process " + p.name)

        response_json = {"response": 'Success! Stopped process ' + p.name}
        return Response(json.dumps(response_json), status=200, mimetype='application/json')
    except Exception as e:
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/start/<process_name>', methods=['GET'])
def start_service(process_name):
    try:
        # get process_name (without additional information)
        process_name = process_name.split(constants.PROCESS_NAME_SPLIT_CHAR)[0]

        if (process_name == constants.PROCESS_ENDLESS_NMAP_SCAN_NAME) or \
                (process_name == constants.PROCESS_ENDLESS_FULL_NETWORK_SCAN_NAME):
            nmap_command = request.args.get('cmd')
            delay = int(request.args.get('delay'))
            if (not nmap_command) or (not delay):
                raise Exception('Missing parameter! Given: cmd=' + str(nmap_command) + ', delay=' + str(delay))

            if process_name == constants.PROCESS_ENDLESS_NMAP_SCAN_NAME:
                service_process = ServiceHandler.start_service(
                    process_name + constants.PROCESS_NAME_SPLIT_CHAR + nmap_command,  # use nmap_command in name
                    NmapService.start_nmap_scan_service,
                    (constants.MONGO_URI, nmap_command, delay,))
            else:  # full scan
                service_process = ServiceHandler.start_service(
                    process_name + constants.PROCESS_NAME_SPLIT_CHAR + nmap_command,  # use nmap_command in name
                    FullScanService.start_full_network_scan_service,
                    (constants.MONGO_URI, nmap_command, delay,))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == constants.PROCESS_ENDLESS_OSQUERY_SCAN_NAME:
            ip_address = request.args.get('ip')
            ssh_port = request.args.get('ssh_port')
            delay = request.args.get('delay')
            if (not ip_address) or (not ssh_port) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) +
                                ', ssh_port=' + str(ssh_port) + ', delay=' + str(delay))

            service_process = ServiceHandler.start_service(
                process_name + constants.PROCESS_NAME_SPLIT_CHAR + ip_address,
                OsqueryService.start_osquery_scan_service,
                (ip_address, int(ssh_port), int(delay),))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == constants.PROCESS_ENDLESS_ZIGBEE2MQTT_STATE_NAME:
            delay = request.args.get('delay')
            if not delay:
                raise Exception('Missing parameter! Given: delay=' + str(delay))

            service_process = ServiceHandler.start_service(
                process_name,
                Zigbee2MqttService.start_zigbee2mqtt_network_state_service,
                (int(delay),))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == constants.PROCESS_ENDLESS_MOSQUITTO_SCAN_NAME:
            ip_address = request.args.get('ip')
            ssh_port = request.args.get('ssh_port')
            delay = request.args.get('delay')
            if (not ip_address) or (not ssh_port) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) + ', ssh_port=' + str(ssh_port) +
                                ', delay=' + str(delay))

            service_process = ServiceHandler.start_service(
                process_name + constants.PROCESS_NAME_SPLIT_CHAR + ip_address,
                MosquittoService.start_mosquitto_service,
                (ip_address, int(ssh_port), int(delay),))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        else:
            response_json = {"response": 'Process not found!'}
            return Response(json.dumps(response_json), status=500, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/available_services', methods=['GET'])
def get_available_services():
    response = {"response": constants.SERVICE_LIST}
    return Response(json.dumps(response), status=200, mimetype='application/json')


@app.route('/running_services', methods=['GET'])
def get_running_services():
    result = ServiceHandler.get_processes()

    array = []
    for service in result:
        if constants.PROCESS_NAME_SPLIT_CHAR in service.name:
            split_name = service.name.split(constants.PROCESS_NAME_SPLIT_CHAR)
            name = split_name[0]
            info = split_name[1]
        else:
            name = service.name
            info = '-'

        array.append({
            'pid': service.pid,
            'name': name,
            'additional_information': info,
            'isalive': service.is_alive()
        })

    response = {"response": array}
    return Response(json.dumps(response), status=200, mimetype='application/json')


@app.route('/network_configuration', methods=['GET', 'POST'])
def get_configuration():
    if request.method == 'GET':
        with open(constants.NETWORK_CONFIGURATION_FILE_NAME, 'r') as file:
            configuration_json = file.read()

        return Response(configuration_json, status=200, mimetype='application/json')
    elif request.method == 'POST':
        with open(constants.NETWORK_CONFIGURATION_FILE_NAME, 'w') as file:
            file.write(request.data.decode('utf-8'))

        response = {"response": request.data.decode('utf-8')}
        return Response(json.dumps(response), status=200, mimetype='application/json')
    else:
        response = {"response": request.data.decode('utf-8')}
        return Response(json.dumps(response), status=405, mimetype='application/json')


@app.route('/analysis/<host_ip>', methods=['GET'])
def execute_analysis(host_ip):  # todo dynamic host finding
    print('Starting analysis for host ' + host_ip)

    should_configuration = ConfigurationHelper.read_should_configuration()

    host_analyser = HostAnalyser(should_configuration, host_ip)
    security_issues_host = host_analyser.analyse()

    security_issues_tmp = []
    # add if not already found
    if security_issues_host is not None and security_issues_host:
        if not any((security_issue.host_ip == host_ip and
                    security_issue.issue_type == SecurityIssueTypes.ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME)
                   for security_issue in security_issues_tmp):
            security_issues_tmp.extend(security_issues_host)

    return Response(json.dumps([ob.__dict__ for ob in security_issues_tmp], cls=ComplexJsonEncoder), status=200,
                    mimetype='application/json')


@app.route('/fix/<host_ip>/<issue_type>', methods=['GET'])
def execute_fix(host_ip, issue_type):
    print('fix ' + host_ip + ' ' + issue_type)

    should_configuration = ConfigurationHelper.read_should_configuration()

    result = None
    if issue_type == SecurityIssueTypes.ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME:
        solver = Zigbee2MqttIssueSolver(should_configuration['zigbee_2_mqtt'])
        result = solver.fix_permit_join(host_ip)
    elif issue_type == SecurityIssueTypes.MOSQUITTO_ACCESS_CONTROL_LIST:
        solver = MosquittoIssueSolver(should_configuration['mosquitto'])
        result = solver.fix_access_control_list(host_ip)

    response = {"response": result}
    return Response(json.dumps(response), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(use_reloader=False)

    # wait for processes to complete
    processes = ServiceHandler.get_processes()
    for process in processes:
        process.join()
