import json
from multiprocessing import Process

from flask import Flask, Response, request
from flask_cors import CORS

import ProcessHandler
import SshHandler
import constants
import jsonHandler
from NmapHandler import NmapHandler

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
        return nmap_handler.get_report_as_json(constants.NMAP_COMMAND_FULL_SCAN_SUFFIX)
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
def start_process(process_name):
    try:
        # get process_name without additional information
        process_name = process_name.split(constants.PROCESS_SPLIT_CHAR)[0]

        if process_name == constants.PROCESS_ENDLESS_NETWORK_SCAN_NAME:
            nmap_command = request.args.get('cmd')
            delay = int(request.args.get('delay'))

            # use nmap_command in name
            p = Process(name=process_name + constants.PROCESS_SPLIT_CHAR + nmap_command,
                        target=ProcessHandler.endless_network_scan,
                        args=(nmap_command, delay,))
            p.start()
            ProcessHandler.process_dict[p.pid] = p

            print("start process " + p.name)

            response_json = {"response": 'Success! Started process ' + p.name}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        elif process_name == 'todo':
            # todo

            response_json = {"response": 'todo'}
            return Response(json.dumps(response_json), status=200, mimetype='application/json')
        else:
            response_json = {"response": 'Process not found!'}
            return Response(json.dumps(response_json), status=500, mimetype='application/json')
    except Exception as e:
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/running_services', methods=['GET'])
def get_running_services():
    result = ProcessHandler.get_processes()

    array = []
    for service in result:
        process_name = service.name.split(constants.PROCESS_SPLIT_CHAR)
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
