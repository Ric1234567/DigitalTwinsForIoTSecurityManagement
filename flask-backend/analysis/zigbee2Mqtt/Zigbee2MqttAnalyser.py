import string

import constants
from analysis import SecurityIssueTypes
from analysis.Recommendation import Recommendation
from analysis.SecurityIssue import SecurityIssue
from handler.HostInformation import HostInformation


# Analysis class for zigbee2mqtt security issues. (ssh required)
class Zigbee2MqttAnalyser:
    def __init__(self, configuration):
        self.configuration = configuration

    # check for the permit join flag
    def compare_permit_join_flag(self, host: HostInformation, host_scan):
        if host_scan['config']['permit_join'] is not self.configuration['permit_join']:
            # build recommendation
            recommendation = Recommendation(constants.ZIGBEE2MQTT,
                                            'The permit_join flag in host ' + str(host.ip) +
                                            ' is not equal to the definition in the should_configuration. ' +
                                            '(host permit_join=' + str(host_scan['config']['permit_join']) +
                                            ', should_configuration permit_join=' +
                                            str(self.configuration['permit_join']) + ')',
                                            'Change the permit_flag to permit_flag=' +
                                            str(self.configuration['permit_join']))

            return SecurityIssue(SecurityIssueTypes.ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME,
                                 host,
                                 recommendation,
                                 SecurityIssueTypes.is_fixable(SecurityIssueTypes.ZIGBEE2MQTT_PERMIT_JOIN_ISSUE_NAME, host))
        else:
            return None
