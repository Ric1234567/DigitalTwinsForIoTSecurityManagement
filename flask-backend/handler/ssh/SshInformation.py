import string


class SshInformation:
    def __init__(self, ip: string, port: int):
        self.ip: string = ip
        self.port: int = port
