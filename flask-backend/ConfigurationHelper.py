import io
import json
import string

import yaml

import constants


def from_yaml_configuration(data):
    fp = io.StringIO(data)
    return yaml.safe_load(fp)


def to_yaml_configuration(data):
    return yaml.dump(data)


def read_should_configuration():
    with open(constants.NETWORK_CONFIGURATION_FILE_NAME, 'r') as file:
        configuration_json = file.read()
        should_configuration = json.loads(configuration_json)
    return should_configuration
