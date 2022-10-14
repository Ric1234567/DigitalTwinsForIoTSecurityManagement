from flask import Flask, jsonify
from flask_cors import CORS
import SshHandler
import constants
import jsonHandler

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/daemon', methods=['GET'])
def get_daemon_output():
    sshHandler = SshHandler.SshHandler(constants.SSH_HOSTNAME, constants.SSH_PORT, constants.SSH_USER,
                                       constants.SSH_PASSWORD)
    sshHandler.connect()

    file_name = "daemon_output.log"
    localpath = '/Users/henrichager/Documents/Studium/Master/SoSe22/masterarbeit-flask-vue/flask-backend/' + file_name
    remotepath = '/home/pi/osquery/logs/osqueryd.results.log'  # check permission of file; needs to be user 'pi'

    sshHandler.get_file_via_sftp(localpath, remotepath)

    with open(file_name, 'r') as file:
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
