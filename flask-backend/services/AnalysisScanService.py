import json
import string
import time
from multiprocessing import Process, current_process

import constants
from analysis.host.HostAnalyser import HostAnalyser
from handler.DatabaseHandler import DatabaseHandler
from handler.HostInformation import HostInformation
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

    def start_analysis_service(self, ip: string, ssh_port: int, delay: int):
        ssh_information = SshInformation(ip, ssh_port)
        host_information = HostInformation(ip=ip, ssh_information=ssh_information)
        should_configuration = ConfigurationHelper.read_network_configuration()

        host_analyser = HostAnalyser(should_configuration, host_information)

        database_handler = DatabaseHandler(constants.MONGO_URI)
        while True:
            print('Start analysis of host ' + str(host_information.ip))

            host_analysis_result = host_analyser.analyse()

            # convert to json
            host_analysis_result_json = json.dumps(host_analysis_result, cls=ComplexJsonEncoder)

            print("Write host analysis of " + str(host_information.ip) + " to database")
            database_handler.insert_one_into(constants.COLLECTION_NAME_HOST_ANALYSIS,
                                             json.loads(host_analysis_result_json))

            print(current_process().name + " sleeping for " + str(delay) + " seconds!")
            time.sleep(delay)
