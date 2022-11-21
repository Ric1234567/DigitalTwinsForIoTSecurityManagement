import json
import string
from multiprocessing import active_children, current_process

from flask import Flask, Response, request
from flask_cors import CORS
from flask_pymongo import PyMongo

from analysis.host.HostAnalysisResult import HostAnalysisResult
from analysis.host.HostSolver import HostSolver
from services import ServiceConstants
from services.AnalysisScanService import AnalysisScanService
from services.CompleteNetworkScanService import CompleteNetworkScanService
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

# Main file of server backend.
# Includes GET and POST methods for the frontend to get management data.

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['MONGO_URI'] = constants.MONGO_URI  # pi database
mongo = PyMongo(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# handler for this file to communicate with the database
database_handler = DatabaseHandler(constants.MONGO_URI)

# array to store all currently running services
running_services = []


# GET method to perform an nmap scan and get the results the scan.
@app.route('/custom_network_scan/<nmap_command>', methods=['GET'])
def get_custom_nmap_report(nmap_command: string):
    nmap_handler = NmapHandler()
    nmap_handler.custom_network_scan(nmap_command)

    # get nmap scan from database
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    # build response json object
    response_json = {
        'response': {
            'nmap_unixTime': nmap_report_db['unixTime'],
            'nmaprun': nmap_report_db['nmaprun']
        }}

    return Response(json.dumps(response_json), status=200, mimetype='application/json')


# GET method for performing and getting an full network scan.
# This includes a nmap scan for all host in the network and all subnetwork of all hosts with ssh.
@app.route('/full_network_scan/<nmap_command>', methods=['GET'])
def get_full_network_report(nmap_command: string):
    nmap_handler = NmapHandler()
    nmap_handler.custom_network_scan(nmap_command)

    # get nmap scan from database
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    # find all hosts in the network with ssh
    ssh_hosts = nmap_handler.ssh_service_discovery(nmap_report_db['nmaprun'])

    subnetwork_handler = SubnetworkHandler()

    # scan the subnetwork for every host with ssh
    for host in ssh_hosts:
        subnetwork_handler.scan_subnetwork_host(host)
    subnetwork, unix_time = subnetwork_handler.get_latest_subnetwork_information()

    # build response json object
    response_json = {
        'response': {
            'nmap_unixTime': nmap_report_db['unixTime'],
            'nmaprun': nmap_report_db['nmaprun'],
            'subnetwork_unixTime': unix_time,
            'subnetwork': subnetwork
        }}

    return Response(json.dumps(response_json), status=200, mimetype='application/json')


# GET method for the last network scan.
@app.route('/last_network_scan', methods=['GET'])
def get_last_network_report():
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    if nmap_report_db is None:
        response_json = {'response': 'No last nmap scan found!'}
        return Response(json.dumps(response_json), status=500, mimetype='application/json')

    subnetwork_handler = SubnetworkHandler()
    subnetwork, unix_time = subnetwork_handler.get_latest_subnetwork_information()

    # build response json object
    response_json = {
        'response': {
            'nmap_unixTime': nmap_report_db['unixTime'],
            'nmaprun': nmap_report_db['nmaprun'],
            'subnetwork_unixTime': unix_time,
            'subnetwork': subnetwork
        }}
    return Response(json.dumps(response_json), status=200, mimetype='application/json')


# GET method for stopping a running service by its pid
@app.route('/stop/<process_pid>', methods=['GET'])
def stop_service(process_pid):
    try:
        for service in running_services:
            if service.process.pid == int(process_pid):
                service.stop()

                # remove service from running list
                running_services.remove(service)
                print('Terminated process ' + service.name + ', pid=' + str(service.process.pid))

                # build response json object
                response_json = {'response': 'Success! Stopped process ' + service.name}
                return Response(json.dumps(response_json), status=200, mimetype='application/json')

    except Exception as e:
        return Response(str(e), status=500, mimetype='application/json')


# GET method for starting a service with a given service_type
@app.route('/start/<service_type>', methods=['GET'])
def start_service(service_type):
    try:
        # get all parameters from the URL (some might be None)
        nmap_command = request.args.get('cmd')
        ip_address = request.args.get('ip')
        ssh_port = request.args.get('ssh_port')
        delay = request.args.get('delay')

        # differentiate between every service type by its name
        if service_type == ServiceConstants.PROCESS_ENDLESS_NMAP_SCAN_NAME:
            if (not nmap_command) or (not delay):
                raise Exception('Missing parameter! Given: cmd=' + str(nmap_command) + ', delay=' + str(delay))

            service = NmapScanService(service_type,
                                      'Nmap-Scan with args: cmd=' +
                                      str(nmap_command) + ', delay=' + str(delay),
                                      (nmap_command, int(delay),))

        elif service_type == ServiceConstants.PROCESS_ENDLESS_COMPLETE_NETWORK_SCAN_NAME:
            if (not nmap_command) or (not delay):
                raise Exception('Missing parameter! Given: cmd=' + str(nmap_command) + ', delay=' + str(delay))

            service = CompleteNetworkScanService(service_type,
                                                 'Complete-Scan with args: cmd=' +
                                                 str(nmap_command) + ', delay=' + str(delay),
                                                 (nmap_command, int(delay),))

        elif service_type == ServiceConstants.PROCESS_ENDLESS_OSQUERY_SCAN_NAME:
            if (not ip_address) or (not ssh_port) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) +
                                ', ssh_port=' + str(ssh_port) + ', delay=' + str(delay))

            service = OsqueryScanService(service_type,
                                         'Osquery-Scan with args: ip=' +
                                         str(ip_address) + ', ssh_port=' + ssh_port + ', delay=' + str(delay),
                                         (ip_address, int(ssh_port), int(delay),))

        elif service_type == ServiceConstants.PROCESS_ENDLESS_ZIGBEE2MQTT_STATE_NAME:
            if (not delay) or (not ip_address) or (not ssh_port):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) +
                                ', ssh_port=' + str(ssh_port) + ', delay=' + str(delay))

            service = Zigbee2MqttScanService(service_type,
                                             'Zigbee2Mqtt-Scan with args: ip=' +
                                             str(ip_address) + ', ssh_port=' + ssh_port + ', delay=' + str(
                                                 delay),
                                             (ip_address, int(ssh_port), int(delay),))

        elif service_type == ServiceConstants.PROCESS_ENDLESS_MOSQUITTO_SCAN_NAME:
            if (not ip_address) or (not ssh_port) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) + ', ssh_port=' + str(ssh_port) +
                                ', delay=' + str(delay))

            service = MosquittoScanService(service_type,
                                           'Mosquitto-Scan with args: ip=' +
                                           str(ip_address) + ', ssh_port=' + ssh_port + ', delay=' + str(
                                               delay),
                                           (ip_address, int(ssh_port), int(delay),))

        elif service_type == ServiceConstants.PROCESS_ENDLESS_ANALYSIS_SCAN_NAME:
            if (not ip_address) or (not delay):
                raise Exception('Missing parameter! Given: ip=' + str(ip_address) + ', delay=' + str(delay))

            service = AnalysisScanService(service_type,
                                          'Analysis-Scan with args: ip=' +
                                          str(ip_address) + ', delay=' + str(delay),
                                          (ip_address, int(delay),))
        else:
            # Process not found if an unknown service_name is given
            response_json = {'response': 'Process not found!'}
            return Response(json.dumps(response_json), status=500, mimetype='application/json')

        # start service
        service.start()
        running_services.append(service)

        # convert to json
        service_json = json.dumps(service, cls=ComplexJsonEncoder)

        response_json = {'response': 'Success! Started process ' + service_json}
        return Response(json.dumps(response_json), status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(str(e), status=500, mimetype='application/json')


# GET method for all available services
@app.route('/available_services', methods=['GET'])
def get_available_services():
    response = {'response': ServiceConstants.SERVICE_LIST}
    return Response(json.dumps(response), status=200, mimetype='application/json')


# GET method for all currently running services
@app.route('/running_services', methods=['GET'])
def get_running_services():
    response = {'response': running_services}
    return Response(json.dumps(response, cls=ComplexJsonEncoder), status=200, mimetype='application/json')


# GET/POST method for getting or updating the network configuration (SOLL-Modell)
@app.route('/network_configuration', methods=['GET', 'POST'])
def get_configuration():
    try:
        if request.method == 'GET':
            with open(constants.NETWORK_CONFIGURATION_FILE_NAME, 'r') as file:
                configuration_json = file.read()

            return Response(configuration_json, status=200, mimetype='application/json')

        elif request.method == 'POST':
            with open(constants.NETWORK_CONFIGURATION_FILE_NAME, 'w') as file:
                file.write(request.data.decode('utf-8'))

            response = {'response': 'Successfully submitted network configuration!'}
            return Response(json.dumps(response), status=200, mimetype='application/json')

        else:
            response = {'response': request.data.decode('utf-8')}
            return Response(json.dumps(response), status=405, mimetype='application/json')
    except FileNotFoundError:
        response_json = {'response': 'No configuration file found!'}
        return Response(json.dumps(response_json), status=500, mimetype='application/json')
    except Exception as e:
        return Response(str(e), status=500, mimetype='application/json')


# GET method for performing an analysis for a given host
@app.route('/analysis/<host_ip>', methods=['GET'])
def get_analysis(host_ip):
    print('Starting analysis for host ' + host_ip)

    should_configuration = ConfigurationHelper.read_network_configuration()

    # scan all ports of host
    nmap_handler = NmapHandler()
    print("Performing Nmap Scan (" + "-sS -T4 -p1-65535 " + host_ip + ", " + current_process().name + ")")
    nmap_handler.custom_network_scan('-sS -T4 -p1-65535 ' + host_ip)

    # get nmap host scan from database
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    # get host information (including ssh information if host supports it)
    host_to_analyse = nmap_handler.get_single_host_including_ssh_information(nmap_report_db['nmaprun'], host_ip)

    if host_to_analyse is None:
        response = {'response': 'Could not find host!'}
        return Response(json.dumps(response), status=500, mimetype='application/json')

    # perform host analysis
    host_analyser = HostAnalyser(should_configuration, host_to_analyse)
    host_analysis_result = host_analyser.analyse()

    # convert to json
    host_analysis_result_json = json.dumps(host_analysis_result, cls=ComplexJsonEncoder)

    print('Write host analysis of ' + host_to_analyse.ip + ' to database')
    database_handler.insert_one_into(constants.COLLECTION_NAME_HOST_ANALYSIS, json.loads(host_analysis_result_json))

    if len(host_analysis_result.security_issues) == 0:
        response = {'response': 'No issues found!'}
        return Response(json.dumps(response), status=200, mimetype='application/json')

    return Response(host_analysis_result_json, status=200, mimetype='application/json')


# GET method for fixing a specific security issue of given host
@app.route('/fix/<host_ip>/<issue_type>', methods=['GET'])
def get_fix(host_ip, issue_type):
    print('Fix ' + host_ip + ' ' + issue_type)

    should_configuration = ConfigurationHelper.read_network_configuration()

    host_solver = HostSolver(should_configuration)
    result = host_solver.solve(host_ip, issue_type)

    response = {'response': result}
    return Response(json.dumps(response), status=200, mimetype='application/json')


# GET method for getting the latest analysis result from the database
@app.route('/latest_analysis_result', methods=['GET'])
def get_latest_analysis_result():
    latest_analysis_result_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_HOST_ANALYSIS)

    if latest_analysis_result_db is None:
        response = {'response': 'No latest analysis found!'}
        return Response(json.dumps(response), status=500, mimetype='application/json')

    latest_analysis_result = HostAnalysisResult(latest_analysis_result_db['host_information'])
    latest_analysis_result.security_issues = latest_analysis_result_db['security_issues']
    latest_analysis_result.unix_time = latest_analysis_result_db['unixTime']

    return Response(json.dumps(latest_analysis_result, cls=ComplexJsonEncoder), status=200, mimetype='application/json')


# GET method for getting all connected hosts in network
@app.route('/ip_hosts', methods=['GET'])
def get_ip_hosts():
    print('Get hosts of last nmaprun...')

    nmap_handler = NmapHandler()
    nmap_handler.custom_network_scan('-sn -T4 ' + constants.IP_NETWORK_PREFIX + '*')

    # get from database
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    hosts = nmap_handler.get_hosts_including_ssh_information(nmap_report_db['nmaprun'])

    return Response(json.dumps([ssh_host.__dict__ for ssh_host in hosts], cls=ComplexJsonEncoder),
                    status=200,
                    mimetype='application/json')


# main function which executes the program
if __name__ == '__main__':
    app.run(use_reloader=False)

    # wait for running_services to complete
    for process in active_children():
        process.join()
