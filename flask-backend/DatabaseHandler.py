import json
import string

import constants


class DatabaseHandler:

    def __init__(self, mongo):
        self.mongo = mongo

    def write_nmaprun_to_database(self, nmap_report_json: string):
        try:
            nmap_report = json.loads(nmap_report_json)
            self.insert_one_into(constants.COLLECTION_NAME_NMAPRUN, nmap_report)
        except Exception as e:
            print(e)
            return

    def write_to_database(self, collection_name: string, data: string):
        data = data.replace(':false,', ':False,').replace(':true,', ':True,')
        data_points = data.split('\n')

        try:
            latest_timestamp = self.get_max_timestamp(collection_name)[0]['unixTime']
        except IndexError:
            latest_timestamp = -1

        for data_point_string in data_points:
            try:
                data_point = eval(data_point_string)

                # filter old entries
                if latest_timestamp >= data_point['unixTime']:
                    continue

                if data_point['name'] == collection_name:
                    self.insert_one_into(collection_name, data_point)
            except Exception as e:
                print('not added: \"' + data_point_string + '\"(' + str(e) + ')')

    def insert_one_into(self, collection_name, data_point):
        self.mongo.db[collection_name].insert_one(data_point)

    def get_max_timestamp(self, collection_name):
        return self.mongo.db[collection_name].find().sort('unixTime', -1).limit(1)

    def select_all(self, collection_name):
        return self.mongo.db[collection_name].find()
