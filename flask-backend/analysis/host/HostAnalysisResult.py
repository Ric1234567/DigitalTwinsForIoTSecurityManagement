import time
import typing

from analysis.SecurityIssue import SecurityIssue
from handler.HostInformation import HostInformation


class HostAnalysisResult:
    def __init__(self, host_information: HostInformation):
        self.security_issues: typing.List[SecurityIssue] = []
        self.unix_time = round(time.time())
        self.host_information = host_information

    def repr_json(self):
        return dict(security_issues=self.security_issues, unix_time=self.unix_time, host_information=self.host_information)
