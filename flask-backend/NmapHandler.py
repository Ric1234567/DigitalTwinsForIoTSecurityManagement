import subprocess


class NmapHandler:
    # cmd = "sudo nmap -oX test.txt -sS -T4 -F 192.168.178.* --traceroute"
    # cmdsimple = "nmap -oX - -sT -T4 192.168.178.51"

    def run_command(self, cmd):
        """
        Runs nmap commands and return xml string
        """
        # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process = subprocess.run(cmd, shell=True, check=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 universal_newlines=True)
        return process.stdout
