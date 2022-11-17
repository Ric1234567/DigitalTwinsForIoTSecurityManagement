import constants
from analysis import SecurityIssueTypes
from analysis.Recommendation import Recommendation
from analysis.SecurityIssue import SecurityIssue
from handler.HostInformation import HostInformation


# Analysis class for ip security issues.
class IpAnalyser:
    def __init__(self, configuration):
        self.configuration = configuration

    # Checks the ports of a given host.
    def check_open_ports(self, host: HostInformation):
        if host is not None and host.ports is not None:
            # check if the open ports exceeds the defined max in the configuration
            if len(host.ports) > int(self.configuration['max_open_ports']):
                # build recommendation for the user
                description = str(len(host.ports)) +\
                              ' open ports on this host found! The maximal allowed amount is ' + \
                              str(self.configuration['max_open_ports']) + '.\n Open Ports: '
                for port in host.ports:
                    description += port['@portid'] + ', '

                recommendation = Recommendation(constants.IP,
                                                description,
                                                'Close unnecessary ports.')

                # create security issue
                return SecurityIssue(SecurityIssueTypes.IP_TOO_MANY_OPEN_PORTS,
                                     recommendation,
                                     SecurityIssueTypes.is_fixable(SecurityIssueTypes.IP_TOO_MANY_OPEN_PORTS, host))
            else:
                print('Open ports check on ' + host.ip + ': Found ' + str(len(host.ports)) + '! STATUS OK')
                return None
