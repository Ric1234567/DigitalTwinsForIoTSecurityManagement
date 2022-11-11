import string

from handler.ssh.SshInformation import SshInformation


class HostInformation:
    def __init__(self, ip: string, hostname: string = None, ssh_information: SshInformation = None):
        self.ip = ip
        self.hostname = hostname
        self.ssh_information = ssh_information

    def repr_json(self):
        return dict(ip=self.ip, hostname=self.hostname, ssh_information=self.ssh_information)
