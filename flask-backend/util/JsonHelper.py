import json
from json import JSONDecodeError

import xmltodict


def filter_json_array(input_json_array, key, value):
    result_array = []

    for element in input_json_array:
        try:
            json_element = json.loads(element)
        except JSONDecodeError:
            continue
        if json_element[key] == value:
            result_array.append(json_element)

    return result_array


def convert_xml_to_json(xml_content):
    json_dict = xmltodict.parse(xml_content)
    return json.dumps(json_dict, indent=4, sort_keys=True)


def convert_xml_file_to_json(xml_path):
    with open(xml_path) as file:
        xml_content = file.read()
    return convert_xml_to_json(xml_content)
