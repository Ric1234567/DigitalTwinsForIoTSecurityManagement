import time

from analysis.host.HostAnalyser import HostAnalyser
from handler.HostInformation import HostInformation
from handler.ssh.SshInformation import SshInformation
from services.OsqueryScanService import execute_osquery_scan
from util import ConfigurationHelper


# Evaluation of osquery device monitoring.
def evaluate_osquery(host_ip, ssh_port):
    # scan ###########################################################
    start_scan = time.time()

    ssh_information = SshInformation(host_ip, ssh_port)
    execute_osquery_scan(ssh_information)

    duration_scan = time.time() - start_scan
    print('Scan ' + str(duration_scan))

    # analysis ###########################################################
    start_analysis = time.time()

    host_information = HostInformation(ip=host_ip, ssh_information=ssh_information)
    # get host information (including ssh information if host supports it)
    should_configuration = ConfigurationHelper.read_network_configuration()
    host_analyser = HostAnalyser(should_configuration, host_information)
    host_analyser.analyse_osquery_information()

    duration_analysis = time.time() - start_analysis
    print('Analysis ' + str(duration_analysis))

    # response ###########################################################
    print('No automatic response available!')

    # complete duration
    print('Sum ' + str(duration_scan + duration_analysis))
