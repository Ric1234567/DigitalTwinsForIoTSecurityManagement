export class HostInformation {
    hostInformationType?: any;

    constructor(hostInformationType?: any) {
        this.hostInformationType = hostInformationType
    }

    getEndtime() {
        return this.hostInformationType?.endtime
    }

    getAddressesString() {
        if (Array.isArray(this.hostInformationType?.address)) {
            let result: string = ''
            for (const address of this.hostInformationType?.address) {
                result += address["@addr"] + '(' + address['@addrtype'] + '), '
            }
            return result
        }
        return this.hostInformationType?.address["@addr"] + '(' + this.hostInformationType?.address['@addrtype'] + ')'
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
        if (Array.isArray(this.hostInformationType?.hostnames)) {
            let result: string = ''
            for (const hostname of this.hostInformationType?.hostnames) {
                result += hostname["@name"] + '(' + hostname['@type'] + '), '
            }
            return result
        }
        return this.hostInformationType?.hostnames.hostname["@name"] + '(' + this.hostInformationType?.hostnames.hostname['@type'] + ')'
    }

    getHostNamesArray() {
        if (Array.isArray(this.hostInformationType?.hostnames)) {
            return this.hostInformationType?.hostnames
        }
        let array = []
        array.push(this.hostInformationType?.hostnames.hostname)
        return array
    }

    getExtraPortsString() {
        let result: string = ''
        if (Array.isArray(this.hostInformationType?.ports.extraports)) {
            for (const extraPort of this.hostInformationType?.ports.extraports) {
                result += extraPort['@count'] + '(' + extraPort['@state'] + '), '
            }
            return result
        }
        return this.hostInformationType?.ports.extraports['@count'] + '(' + this.hostInformationType?.ports.extraports['@state'] + ')'
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
        let result: string = ''
        if (Array.isArray(this.hostInformationType?.ports.port)) {
            for (const extraPort of this.hostInformationType?.ports.port) {
                result += extraPort['@portid'] + '(' + extraPort['@protocol'] + '), '
            }
            return result
        }
        return this.hostInformationType?.ports.port['@portid'] + '(' + this.hostInformationType?.ports.port['@protocol'] + ')'
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
        if (Array.isArray(this.hostInformationType?.trace)) {
            return this.hostInformationType?.trace
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