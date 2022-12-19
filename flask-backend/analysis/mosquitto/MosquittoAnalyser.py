import collections

import constants
from analysis import SecurityIssueTypes
from analysis.Recommendation import Recommendation
from analysis.SecurityIssue import SecurityIssue
from handler.HostInformation import HostInformation


def remove_unnecessary_lines(lines):
    result = []
    for line in lines:
        # filter empty or comment line
        if line != '' and line[0] != '#':
            result.append(line)

    return result


# Analysis class for mosquitto security issues. (ssh required)
class MosquittoAnalyser:
    def __init__(self, configuration):
        self.configuration = configuration

    # check for the acl configuration
    def compare_access_control_list(self, host: HostInformation, host_configuration):
        # preprocessing configurations
        topics = host_configuration['acl'].split('\n')
        topics = remove_unnecessary_lines(topics)

        should_topics = self.configuration['acl'].split('\n')
        should_topics = remove_unnecessary_lines(should_topics)

        # remove useless spaces
        topics = [topic.strip() for topic in topics]
        should_topics = [should_topic.strip() for should_topic in should_topics]

        # check if they contain the same elements
        if collections.Counter(topics) != collections.Counter(should_topics):
            # build recommendation
            recommendation = Recommendation(constants.MOSQUITTO,
                                            'The access control list for accessible topics is not equal to ' +
                                            'the defined default configuration and may be unsecure.\n[\n' +
                                            str(host_configuration['acl'].strip() + '\n]'),
                                            'Consider using the default configuration.\n[\n' +
                                            str(self.configuration['acl'].strip() + '\n]'))

            return SecurityIssue(SecurityIssueTypes.MOSQUITTO_ACCESS_CONTROL_LIST,
                                 recommendation,
                                 SecurityIssueTypes.is_fixable(SecurityIssueTypes.MOSQUITTO_ACCESS_CONTROL_LIST, host))

        print('ACL check on ' + host.ip + ': STATUS OK')
        return None
