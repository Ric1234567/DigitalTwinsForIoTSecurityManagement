import string

from analysis.Recommendation import Recommendation
from handler.HostInformation import HostInformation


# Class which holds data to security issues with its type and recommendation.
class SecurityIssue:

    def __init__(self, issue_type: string, recommendation: Recommendation, fixable: bool):
        self.issue_type = issue_type
        self.recommendation = recommendation
        self.fixable = fixable

    def repr_json(self):
        return dict(issue_type=self.issue_type, recommendation=self.recommendation, fixable=self.fixable)
