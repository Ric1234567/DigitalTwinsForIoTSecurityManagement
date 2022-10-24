import json
import string
from multiprocessing import Process

from flask import Flask, Response, request
from flask_cors import CORS
from flask_pymongo import PyMongo

import ProcessHandler
import SshHandler
import constants
import JsonHandler
from DatabaseHandler import DatabaseHandler
from NmapHandler import NmapHandler

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
def get_custom_network_report(nmap_command: string):
    try:
        nmap_handler = NmapHandler()
        nmap_report_json = nmap_handler.get_report_as_json(nmap_command)

        # save to database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        database_handler.write_nmaprun_to_database(nmap_report_json)

        return nmap_report_json
    except FileNotFoundError as e:
        return Response(str(e), status=404, mimetype='application/json')


@app.route('/network_scan', methods=['GET'])
def get_network_report():
    try:
        return get_custom_network_report(constants.NMAP_COMMAND_FULL_SCAN_SUFFIX)
    except FileNotFoundError as e:
        return Response(str(e), status=404, mimetype='application/json')


@app.route('/last_network_scan', methods=['GET'])
def get_last_network_report():
    try:
        nmap_handler = NmapHandler()
        return nmap_handler.load_report_as_json()
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

        if process_name == constants.PROCESS_ENDLESS_NETWORK_SCAN_NAME:
            nmap_command = request.args.get('cmd')
            delay = int(request.args.get('delay'))
            if (not nmap_command) or (not delay):
                raise Exception('Missing parameter! Given: cmd=' + str(nmap_command) + ', delay=' + str(delay))

            # use nmap_command in name
            service_process = ProcessHandler.start_process(
                process_name + constants.PROCESS_NAME_SPLIT_CHAR + nmap_command,
                ProcessHandler.endless_network_scan,
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
