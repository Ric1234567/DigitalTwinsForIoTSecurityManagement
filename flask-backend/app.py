import json
import string

from flask import Flask, Response, request
from flask_cors import CORS
from flask_pymongo import PyMongo

from analysis.host.HostSolver import HostSolver
from services import NmapService, FullScanService, OsqueryService, Zigbee2MqttService, MosquittoService, \
    ServiceConstants
from util import ConfigurationHelper
from util.ComplexJsonEncoder import ComplexJsonEncoder
from analysis.host.HostAnalyser import HostAnalyser
from handler import ServiceHandler
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
        process_name = process_name.split(ServiceConstants.PROCESS_NAME_SPLIT_CHAR)[0]

        if (process_name == ServiceConstants.PROCESS_ENDLESS_NMAP_SCAN_NAME) or \
                (process_name == ServiceConstants.PROCESS_ENDLESS_FULL_NETWORK_SCAN_NAME):
            nmap_command = request.args.get('cmd')
            delay = request.args.get('delay')
            if (not nmap_command) or (not delay):
                raise Exception('Missing parameter! Given: cmd=' + str(nmap_command) + ', delay=' + str(delay))

            if process_name == ServiceConstants.PROCESS_ENDLESS_NMAP_SCAN_NAME:
                service_process = ServiceHandler.start_service(
                    process_name + ServiceConstants.PROCESS_NAME_SPLIT_CHAR + nmap_command,  # use nmap_command in name
                    NmapService.start_nmap_scan_service,
                    (nmap_command, int(delay),))
            else:  # full scan
                service_process = ServiceHandler.start_service(
                    process_name + ServiceConstants.PROCESS_NAME_SPLIT_CHAR + nmap_command,  # use nmap_command in name
                    FullScanService.start_full_network_scan_service,
                    (nmap_command, int(delay),))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == ServiceConstants.PROCESS_ENDLESS_OSQUERY_SCAN_NAME:
            ip_address = request.args.get('ip')
            ssh_port = request.args.get('ssh_port')
            delay = request.args.get('delay')
            if (not ip_address) or (not ssh_port) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) +
                                ', ssh_port=' + str(ssh_port) + ', delay=' + str(delay))

            service_process = ServiceHandler.start_service(
                process_name + ServiceConstants.PROCESS_NAME_SPLIT_CHAR + ip_address,
                OsqueryService.start_osquery_scan_service,
                (ip_address, int(ssh_port), int(delay),))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == ServiceConstants.PROCESS_ENDLESS_ZIGBEE2MQTT_STATE_NAME:
            ip_address = request.args.get('ip')
            ssh_port = request.args.get('ssh_port')
            delay = request.args.get('delay')
            if (not delay) or (not ip_address) or (not ssh_port):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) +
                                ', ssh_port=' + str(ssh_port) + ', delay=' + str(delay))

            service_process = ServiceHandler.start_service(
                process_name + ServiceConstants.PROCESS_NAME_SPLIT_CHAR + ip_address,
                Zigbee2MqttService.start_zigbee2mqtt_network_state_service,
                (ip_address, ssh_port, int(delay),))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == ServiceConstants.PROCESS_ENDLESS_MOSQUITTO_SCAN_NAME:
            ip_address = request.args.get('ip')
            ssh_port = request.args.get('ssh_port')
            delay = request.args.get('delay')
            if (not ip_address) or (not ssh_port) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) + ', ssh_port=' + str(ssh_port) +
                                ', delay=' + str(delay))

            service_process = ServiceHandler.start_service(
                process_name + ServiceConstants.PROCESS_NAME_SPLIT_CHAR + ip_address,
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
    response = {"response": ServiceConstants.SERVICE_LIST}
    return Response(json.dumps(response), status=200, mimetype='application/json')


@app.route('/running_services', methods=['GET'])
def get_running_services():
    result = ServiceHandler.get_processes()

    array = []
    for service in result:
        if ServiceConstants.PROCESS_NAME_SPLIT_CHAR in service.name:
            split_name = service.name.split(ServiceConstants.PROCESS_NAME_SPLIT_CHAR)
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

    if len(host_analysis_result.security_issues) == 0:
        response = {"response": "No issues found!"}
        return Response(json.dumps(response), status=200, mimetype='application/json')

    return Response(json.dumps(host_analysis_result, cls=ComplexJsonEncoder), status=200,
                    mimetype='application/json')


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

    # wait for processes to complete
    processes = ServiceHandler.get_processes()
    for process in processes:
        process.join()
