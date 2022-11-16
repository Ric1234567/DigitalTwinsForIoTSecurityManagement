import string

import paramiko


# Class which manages ssh related operations.
class SshHandler:

    def __init__(self, hostname, port, user, password):
        self.host = hostname
        self.port = port
        self.user = user
        self.password = password
        self.ssh_client = paramiko.SSHClient()

    # connect to ssh server
    def connect(self):
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=self.host, port=self.port, username=self.user, password=self.password)

    # disconnect from ssh server
    def disconnect(self):
        self.ssh_client.close()

    # read remote file via sftp.
    def read_file_content_via_sftp(self, file_path):
        sftp = self.ssh_client.open_sftp()

        with sftp.open(file_path, 'r') as remote_file:
            content = remote_file.read()
            remote_file.close()
        sftp.close()

        return content

    # write string to remote file via sftp
    def write_file_content_via_sftp(self, file_path, content):
        sftp = self.ssh_client.open_sftp()

        with sftp.open(file_path, 'w') as remote_file:
            remote_file.write(content)
            remote_file.close()
        sftp.close()

    # download a remote file via sftp
    def download_file_via_sftp(self, local_path, remote_path):
        sftp = self.ssh_client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    # download a remote file via sftp and delete its content on the ssh device
    def download_file_delete_content_via_sftp(self, local_path, remote_path):
        sftp = self.ssh_client.open_sftp()
        sftp.get(remote_path, local_path)

        with sftp.open(remote_path, 'w') as remote_file:
            remote_file.write("")  # delete content (file needs user rights, they remain untouched)
            remote_file.close()
        sftp.close()

    # put a file to an ssh device
    def upload_file_via_sftp(self, local_path, remote_path):
        sftp = self.ssh_client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    # execute command while being connected to an ssh device
    def execute_command(self, command: string):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        stdout.channel.set_combine_stderr(True)
        output = stdout.readlines()
        return output
