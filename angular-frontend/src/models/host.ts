import { SshInformation } from "./sshInformation"

export class Host {
    ip: string
    hostname: string
    ssh_information: SshInformation

    constructor(ip: string, hostname: string, ssh_information: SshInformation) {
        this.ip = ip
        this.hostname = hostname
        this.ssh_information = ssh_information
    }
}