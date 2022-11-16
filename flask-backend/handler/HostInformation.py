import string

from handler.ssh.SshInformation import SshInformation


# class which holds information of a host. The data is filled by an nmap scan
class HostInformation:
    def __init__(self, ip: string, hostname: string = None, ports=None, ssh_information: SshInformation = None):
        self.ip = ip
        self.hostname = hostname
        self.ports = ports
        self.ssh_information = ssh_information

    def repr_json(self):
        return dict(ip=self.ip, hostname=self.hostname, ports=self.ports, ssh_information=self.ssh_information)
