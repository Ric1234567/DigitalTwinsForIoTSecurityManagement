import paramiko


class SshHandler:

    def __init__(self, hostname, port, user, password):
        self.host = hostname
        self.port = port
        self.user = user
        self.password = password
        self.ssh_client = paramiko.SSHClient()

    def connect(self):
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=self.host, port=self.port, username=self.user, password=self.password)

        # execute command
        # _stdin, _stdout, _stderr = ssh_client.exec_command("ls -l")
        # print(_stdout.read().decode())

    def disconnect(self):
        self.ssh_client.close()

    def get_file_via_sftp(self, local_path, remote_path):
        sftp = self.ssh_client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
