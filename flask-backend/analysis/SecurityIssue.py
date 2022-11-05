import string

from analysis.Recommendation import Recommendation


class SecurityIssue:

    def __init__(self, issue_type: string, host_ip: string, recommendation: Recommendation):
        self.issue_type = issue_type
        self.host_ip = host_ip
        self.recommendation = recommendation

    def repr_json(self):
        return dict(issue_type=self.issue_type, host_ip=self.host_ip, recommendation=self.recommendation)
