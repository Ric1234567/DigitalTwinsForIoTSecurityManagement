import json
from json import JSONDecodeError


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
