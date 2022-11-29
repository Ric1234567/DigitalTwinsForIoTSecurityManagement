export class HostInformation {
    hostInformationType?: any;

    constructor(hostInformationType?: any) {
        this.hostInformationType = hostInformationType
    }

    getEndtime() {
        return this.hostInformationType?.endtime
    }

    getAddressesString() {
        let addresses = this.getAddressesArray()
        return addresses.map((x: any) => x["@addr"]).join(', ')
    }

    getAddressesArray() {
        if (Array.isArray(this.hostInformationType?.address)) {
            return this.hostInformationType?.address
        }
        let array = []
        array.push(this.hostInformationType?.address)
        return array
    }

    getHostNamesString() {
        let hostnames = this.getHostNamesArray()
        return hostnames.map((x: any) => x['@name']).join(', ')
    }

    getHostNamesArray() {
        if (Array.isArray(this.hostInformationType?.hostnames)) {
            return this.hostInformationType?.hostnames
        }
        if (Array.isArray(this.hostInformationType?.hostnames?.hostname)) {
            return this.hostInformationType?.hostnames?.hostname
        }
        let array = []
        array.push(this.hostInformationType?.hostnames.hostname)
        return array
    }

    getExtraPortsString() {
        let ports = this.getExtraPortsArray()
        return ports.map((x: any) => x['@count']).join(', ')
    }

    getExtraPortsArray() {
        if (Array.isArray(this.hostInformationType?.ports.extraports)) {
            return this.hostInformationType?.ports.extraports
        }
        let array = []
        array.push(this.hostInformationType?.ports.extraports)
        return array
    }

    getOpenPortsString() {
        let openPorts = this.getOpenPortsArray()
        return openPorts.map((x:any) => x['@portid']).join(', ')
    }

    getOpenPortsArray() {
        if (Array.isArray(this.hostInformationType?.ports.port)) {
            return this.hostInformationType?.ports.port
        }
        let array = []
        array.push(this.hostInformationType?.ports.port)
        return array
    }

    getStatusString() {
        return this.hostInformationType?.status['@reason']
    }

    getTraceArray() {
        if (Array.isArray(this.hostInformationType?.trace?.hop)) {
            return this.hostInformationType?.trace?.hop
        }
        let array = []
        array.push(this.hostInformationType?.trace.hop)
        return array
    }

    getOsArray() {
        if (Array.isArray(this.hostInformationType?.os?.osmatch)) {
            return this.hostInformationType?.os?.osmatch
        }
        let array = []
        array.push(this.hostInformationType?.os?.osmatch)
        return array
    }
}