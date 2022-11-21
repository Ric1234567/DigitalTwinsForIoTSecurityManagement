import json
import string
import time
from multiprocessing import Process, current_process

import constants
from analysis.host.HostAnalyser import HostAnalyser
from handler.DatabaseHandler import DatabaseHandler
from handler.HostInformation import HostInformation
from handler.NmapHandler import NmapHandler
from handler.ssh.SshInformation import SshInformation
from services.Service import Service
from util import ConfigurationHelper
from util.ComplexJsonEncoder import ComplexJsonEncoder


class AnalysisScanService(Service):

    def __init__(self, name: string, description: string, args: tuple):
        process = Process(name=name,
                          target=self.start_analysis_service,
                          args=args)
        super().__init__(name, description, args, process)

    def start_analysis_service(self, ip: string, delay: int):
        nmap_handler = NmapHandler()

        should_configuration = ConfigurationHelper.read_network_configuration()

        database_handler = DatabaseHandler(constants.MONGO_URI)
        while True:
            print('Start analysis of host ' + ip)

            print("Performing Nmap Scan (-sS -T4 -p1-65535 " + ip + ", " + current_process().name + ")")
            nmap_handler.custom_network_scan("-sS -T4 -p1-65535 " + ip)

            # get from database
            nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

            host_to_analyse = nmap_handler.get_single_host_including_ssh_information(nmap_report_db['nmaprun'], ip)

            if host_to_analyse is None:
                raise Exception('Cannot find host! It might be down.')

            host_analyser = HostAnalyser(should_configuration, host_to_analyse)
            host_analysis_result = host_analyser.analyse()

            # convert to json
            host_analysis_result_json = json.dumps(host_analysis_result, cls=ComplexJsonEncoder)

            print("Write host analysis of " + ip + " to database")
            database_handler.insert_one_into(constants.COLLECTION_NAME_HOST_ANALYSIS,
                                             json.loads(host_analysis_result_json))

            print(current_process().name + " sleeping for " + str(delay) + " seconds!")
            time.sleep(delay)
