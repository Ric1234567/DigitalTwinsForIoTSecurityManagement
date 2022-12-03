import json
import time

import constants
from analysis import SecurityIssueTypes
from analysis.host.HostAnalyser import HostAnalyser
from analysis.host.HostAnalysisResult import HostAnalysisResult
from analysis.host.HostSolver import HostSolver
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from util import ConfigurationHelper
from util.ComplexJsonEncoder import ComplexJsonEncoder


# Evaluation for the port analysis.
def evaluate_port(host_ip):
    # scan ###########################################################
    start_scan = time.time()

    nmap_handler = NmapHandler()
    nmap_handler.custom_network_scan('-sS -T4 -p1-65535 ' + host_ip)
    database_handler = DatabaseHandler(constants.MONGO_URI)
    nmap_report_db = database_handler.select_latest_entry(constants.COLLECTION_NAME_NMAPRUN)

    duration_scan = time.time() - start_scan
    print('Scan ' + str(duration_scan))

    # analysis ###########################################################
    start_analysis = time.time()

    host_to_analyse = nmap_handler.get_single_host_including_ssh_information(nmap_report_db['nmaprun'], host_ip)
    should_configuration = ConfigurationHelper.read_network_configuration()
    host_analyser = HostAnalyser(should_configuration, host_to_analyse)
    security_issue = host_analyser.ip_analysis()
    host_analysis_result = HostAnalysisResult(host_to_analyse)
    host_analysis_result_json = json.dumps(host_analysis_result, cls=ComplexJsonEncoder)

    duration_analysis = time.time() - start_analysis
    print('Analysis ' + str(duration_analysis))

    # response ###########################################################
    start_response = time.time()

    host_solver = HostSolver(should_configuration)
    status = host_solver.solve(host_ip, SecurityIssueTypes.IP_TOO_MANY_OPEN_PORTS)
    print(status)

    duration_response = time.time() - start_response
    print('Response ' + str(duration_response))

    # complete duration
    print('Sum ' + str(duration_scan + duration_analysis + duration_response))
