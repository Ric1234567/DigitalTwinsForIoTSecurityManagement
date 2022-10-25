import json
import string

from flask import Flask, Response, request
from flask_cors import CORS
from flask_pymongo import PyMongo

import ProcessHandler
from SubnetworkHandler import SubnetworkHandler
import constants
import JsonHandler
from DatabaseHandler import DatabaseHandler
from NmapHandler import NmapHandler

import io
import yaml

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

    subnetwork_handler = SubnetworkHandler()
    subnetwork_handler.scan_subnetwork()
    subnetwork = subnetwork_handler.get_latest_subnetwork_information()

    response_json = {
        "response": {
            'nmaprun': nmap_report_db['nmaprun'],
            'subnetwork': subnetwork
        }}
    return Response(json.dumps(response_json), status=200, mimetype='application/json')


@app.route('/last_network_scan', methods=['GET'])
def get_last_network_report():
    try:
        database_handler = DatabaseHandler(constants.MONGO_URI)
        nmap_report_db = database_handler.get_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

        subnetwork_handler = SubnetworkHandler()
        subnetwork = subnetwork_handler.get_latest_subnetwork_information()

        response_json = {
            "response": {
                'nmaprun': nmap_report_db['nmaprun'],
                'subnetwork': subnetwork
            }}
        return Response(json.dumps(response_json), status=200, mimetype='application/json')
    except FileNotFoundError as e:
        return Response(str(e), status=404, mimetype='application/json')


@app.route('/processes', methods=['GET'])
def get_processes():
    json_data = ProcessHandler.download_osquery_output_file()
    return JsonHandler.filter_json_array(json_data.split('\n'), 'name', 'processes')


@app.route('/listening_ports', methods=['GET'])
def get_listening_ports():
    json_data = ProcessHandler.download_osquery_output_file()
    return JsonHandler.filter_json_array(json_data.split('\n'), 'name', 'listening_ports')


@app.route('/stop/<process_pid>', methods=['GET'])
def stop_process(process_pid):
    try:
        p = ProcessHandler.process_dict.pop(int(process_pid))
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
                service_process = ProcessHandler.start_process(
                    process_name + constants.PROCESS_NAME_SPLIT_CHAR + nmap_command,  # use nmap_command in name
                    ProcessHandler.endless_nmap_scan,
                    (constants.MONGO_URI, nmap_command, delay,))
            else:  # full scan
                service_process = ProcessHandler.start_process(
                    process_name + constants.PROCESS_NAME_SPLIT_CHAR + nmap_command,  # use nmap_command in name
                    ProcessHandler.endless_full_network_scan,
                    (constants.MONGO_URI, nmap_command, delay,))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == constants.PROCESS_ENDLESS_OSQUERY_SCAN_NAME:
            delay = int(request.args.get('delay'))

            service_process = ProcessHandler.start_process(
                process_name + constants.PROCESS_NAME_SPLIT_CHAR + constants.SSH_HOSTNAME,
                ProcessHandler.endless_osquery_scan,
                (constants.SSH_HOSTNAME, delay,))

            response_json = {"response": 'Success! Started process ' + service_process.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == constants.PROCESS_ENDLESS_ZIGBEE2MQTT_STATE_NAME:
            delay = int(request.args.get('delay'))

            service_process = ProcessHandler.start_process(
                process_name + constants.PROCESS_NAME_SPLIT_CHAR + constants.SSH_HOSTNAME,
                ProcessHandler.endless_get_zigbee2mqtt_network_state,
                (delay,))

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
    response = {"response": constants.PROCESS_LIST}
    return Response(json.dumps(response), status=200, mimetype='application/json')


@app.route('/running_services', methods=['GET'])
def get_running_services():
    result = ProcessHandler.get_processes()

    array = []
    for service in result:
        process_name = service.name.split(constants.PROCESS_NAME_SPLIT_CHAR)
        array.append({
            'pid': service.pid,
            'name': process_name[0],
            'additional_information': process_name[1],
            'isalive': service.is_alive()
        })

    response = {"response": array}
    return Response(json.dumps(response), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(use_reloader=False)

    # wait for processes to complete
    processes = ProcessHandler.get_processes()
    for process in processes:
        process.join()
