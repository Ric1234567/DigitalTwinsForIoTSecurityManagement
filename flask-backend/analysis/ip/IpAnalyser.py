import string

import constants
from analysis import SecurityIssueTypes
from analysis.Recommendation import Recommendation
from analysis.SecurityIssue import SecurityIssue
from handler.HostInformation import HostInformation
from handler.NmapHandler import NmapHandler


class IpAnalyser:
    def __init__(self, configuration):
        self.configuration = configuration

    def check_open_ports(self, host: HostInformation):
        if host is not None and host.ports is not None:
            if len(host.ports) > int(self.configuration['max_open_ports']):
                description = str(len(host.ports)) +\
                              ' open ports on this host found! The maximal allowed amount is ' + \
                              str(self.configuration['max_open_ports']) + '.\n Open Ports: '
                for port in host.ports:
                    description += port['@portid'] + ', '

                recommendation = Recommendation(constants.IP,
                                                description,
                                                'Close unnecessary ports.')
                return SecurityIssue(SecurityIssueTypes.IP_TOO_MANY_OPEN_PORTS,
                                     host,
                                     recommendation,
                                     SecurityIssueTypes.is_fixable(SecurityIssueTypes.IP_TOO_MANY_OPEN_PORTS, host))
            else:
                print('Open ports check: Found ' + str(len(host.ports)) + '! OK')
                return None
