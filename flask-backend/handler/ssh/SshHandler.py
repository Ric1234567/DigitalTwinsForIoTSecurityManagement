import string

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

    def read_file_content_via_sftp(self, file_path):
        sftp = self.ssh_client.open_sftp()

        with sftp.open(file_path, 'r') as remote_file:
            content = remote_file.read()
            remote_file.close()
        sftp.close()

        return content

    def write_file_content_via_sftp(self, file_path, content):
        sftp = self.ssh_client.open_sftp()

        with sftp.open(file_path, 'w') as remote_file:
            remote_file.write(content)
            remote_file.close()
        sftp.close()

    def download_file_via_sftp(self, local_path, remote_path):
        sftp = self.ssh_client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    def download_file_delete_content_via_sftp(self, local_path, remote_path):
        sftp = self.ssh_client.open_sftp()
        sftp.get(remote_path, local_path)

        with sftp.open(remote_path, 'w') as remote_file:
            remote_file.write("")  # delete content (file needs user rights, they remain untouched)
            remote_file.close()
        sftp.close()

    def upload_file_via_sftp(self, local_path, remote_path):
        sftp = self.ssh_client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def execute_command(self, command: string):
        return self.ssh_client.exec_command(command)
