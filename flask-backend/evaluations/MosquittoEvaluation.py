import time

import constants
from analysis import SecurityIssueTypes
from analysis.host.HostAnalyser import HostAnalyser
from analysis.host.HostSolver import HostSolver
from handler.DatabaseHandler import DatabaseHandler
from handler.HostInformation import HostInformation
from handler.NmapHandler import NmapHandler
from handler.ssh.SshInformation import SshInformation
from services.MosquittoScanService import execute_mosquitto_scan
from util import ConfigurationHelper


# Evaluation of mosquitto scan, analysis, response.
def evaluate_mosquitto(host_ip, ssh_port):
    # scan ###########################################################
    start_scan = time.time()

    ssh_information = SshInformation(host_ip, ssh_port)
    execute_mosquitto_scan(ssh_information)

    duration_scan = time.time() - start_scan
    print('Scan ' + str(duration_scan))

    # analysis ###########################################################
    start_analysis = time.time()

    host_information = HostInformation(ip=host_ip, ssh_information=ssh_information)
    # get host information (including ssh information if host supports it)
    should_configuration = ConfigurationHelper.read_network_configuration()
    host_analyser = HostAnalyser(should_configuration, host_information)
    host_analyser.analyse_mosquitto()

    duration_analysis = time.time() - start_analysis
    print('Analysis ' + str(duration_analysis))

    # response ###########################################################
    start_response = time.time()

    host_solver = HostSolver(should_configuration)
    status = host_solver.solve(host_ip, SecurityIssueTypes.MOSQUITTO_ACCESS_CONTROL_LIST)

    duration_response = time.time() - start_response
    print('Response ' + str(duration_response))

    # complete duration
    print('Sum ' + str(duration_scan + duration_analysis + duration_response))

