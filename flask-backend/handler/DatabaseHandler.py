import array
import json
import string
import time

from flask_pymongo import MongoClient

import constants
from handler.ssh.SshInformation import SshInformation


def filter_data_points_for_collection(collection_name: string, data_points: array):
    result = []
    for data_point in data_points:
        if data_point['name'] == collection_name:
            result.append(data_point)
    return result


class DatabaseHandler:

    def __init__(self, mongo_uri):
        self.mongo = MongoClient(mongo_uri)  # here mongo_client; but parameter is string to mongodb server

    @staticmethod
    def preprocess_data_string(data: string):
        data = data.replace(':false,', ':False,').replace(':true,', ':True,')
        data = data.split('\n')

        data_points = []
        for data_point_string in data:
            try:
                data_point = eval(data_point_string)
                data_points.append(data_point)
            except Exception as e:
                print(e)
        return data_points

    def write_nmaprun_to_database(self, nmap_report_json: string):
        try:
            test = '{"unixTime":' + str(round(time.time())) + ',' + nmap_report_json[1:-1] + '}'
            nmap_report = json.loads(test)
            self.insert_one_into(constants.COLLECTION_NAME_NMAPRUN, nmap_report)
        except Exception as e:
            print(e)
            return

    def write_all_to_database(self, collection_name: string, data: string, ssh_information: SshInformation):
        data_points = self.preprocess_data_string(data)
        data_points = filter_data_points_for_collection(collection_name, data_points)

        # add ip
        for data_point in data_points:
            data_point['host_ip'] = ssh_information.ip

        if len(data_points) > 0:
            result = self.insert_many_into(collection_name, data_points)
            print(str(len(result.inserted_ids)) + " new items in " + collection_name)

    def insert_many_into(self, collection_name, data_points):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].insert_many(data_points)

    def insert_one_into(self, collection_name, data_point):
        self.mongo[constants.PI_DATABASE_NAME][collection_name].insert_one(data_point)

    def get_max_timestamp(self, collection_name):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].find().sort('unixTime', -1).limit(1)

    def get_latest_entry(self, collection_name):
        cursor = self.get_max_timestamp(collection_name)
        for entry in cursor:
            return entry

    def get_latest_zigbee2mqtt_entry_of_host(self, host_ip):
        cursor = self.mongo[constants.PI_DATABASE_NAME][constants.COLLECTION_NAME_ZIGBEE2MQTT_NETWORK_STATE]\
            .find({'scans.host': host_ip}).sort('unixTime', -1).limit(1)
        for entry in cursor:
            return entry

    def get_latest_mosquitto_entry_of_host(self, host_ip):
        cursor = self.mongo[constants.PI_DATABASE_NAME][constants.COLLECTION_NAME_MOSQUITTO_CONFIG]\
            .find({'host': host_ip}).sort('unixTime', -1).limit(1)
        for entry in cursor:
            return entry

    def select_all(self, collection_name):
        return self.mongo[constants.PI_DATABASE_NAME][collection_name].find()
