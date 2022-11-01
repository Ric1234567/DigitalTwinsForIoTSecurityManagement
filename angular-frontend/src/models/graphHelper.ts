import GraphLink from "./graphLink";
import GraphNode from "./graphNode";

type AverageRtt = {
    min: number
    max: number
}

type GraphContent = {
    nodeList: GraphNode[]
    linkList: GraphLink[]
}

export default class GraphHelper {
    nodeList: GraphNode[] = []
    linkList: GraphLink[] = []
    averageRtt: AverageRtt = { min: -1, max: -1 }


    getGraphContent(nmaprun: any, subnetwork: any, nodeColorstyle: string): GraphContent {
        if (!Array.isArray(nmaprun.host)) {
            let tmpArray = []
            tmpArray.push(nmaprun.host)
            nmaprun.host = tmpArray
        }

        if (nmaprun.host != null) {
            this.averageRtt = GraphHelper.getMaxMinRtt(nmaprun)
        }

        nmaprun.host.forEach((host: any) => {
            let hostIp = ""
            if (Array.isArray(host.address)) {
                hostIp = host.address[0]["@addr"]
            } else {
                hostIp = host.address["@addr"]
            }

            let hostNameIp = hostIp + (host.hostnames?.hostname["@name"] ? '\n(' + host.hostnames?.hostname["@name"] + ')' : '')

            let tmpNode: GraphNode
            // color / open ports
            if (nodeColorstyle === 'Port Count'){
                let nodeColor = GraphHelper.getNodeColorOnPorts(host)
                tmpNode = new GraphNode(hostNameIp, nodeColor)
            } else {
                tmpNode = new GraphNode(hostNameIp, 'FireBrick')
            }

            // add if it does not exist already
            if (this.nodeList.filter(node => node.name === tmpNode.name)) {
                this.nodeList.push(tmpNode)
            }

            // links / traces / hops
            this.getTraces(host, hostNameIp)

            // subnetwork
            if (subnetwork) {
                for (const subnetworkDevice of subnetwork) {
                    if (subnetworkDevice.host === hostIp) {
                        let subnetworkDeviceName = subnetworkDevice.name + '\n' + subnetworkDevice.hex

                        let nodeColor: string
                        if (nodeColorstyle === 'Port Count') {
                            nodeColor = 'gray'
                        } else {
                            nodeColor = 'teal'
                        }

                        let tmpNode: GraphNode = new GraphNode(subnetworkDeviceName, nodeColor)
                        // add if it does not exist already
                        if (this.nodeList.filter(node => node.name === tmpNode.name)) {
                            this.nodeList.push(tmpNode)
                        }

                        let tmpLink = new GraphLink(hostNameIp, subnetworkDeviceName)
                        // if it does not link to itself
                        if (tmpLink.source != tmpLink.target) {
                            this.linkList.push(tmpLink)
                        }
                    }
                }
            }
        });

        let localhostNode = new GraphNode("localhost", "#000")
        this.nodeList.push(localhostNode)

        return { nodeList: this.nodeList, linkList: this.linkList }
    }

    addNodesFoundInTraces(targetName: string) {
        var found = false;
        for (var i = 0; i < this.nodeList.length; i++) {
            if (this.nodeList[i].name == targetName) {
                found = true;
                break;
            }
        }

        if (!found) {
            let tmpNode = {
                name: targetName,
                label: {
                    show: true
                },
                itemStyle: {
                    color: "#535353",
                    borderWidth: 1
                }
            }
            this.nodeList.push(tmpNode)
        }
    }

    getTraces(host: any, hostNameIp: string) {
        if (host.trace != null) {
            let targetName = ""
            let lastHop: string = "localhost"

            let hops = []
            if (Array.isArray(host.trace.hop)) {
                hops = host.trace.hop
            } else {
                hops.push(host.trace.hop)
            }
            hops.forEach((hop: any) => {
                targetName = hop["@ipaddr"] + (hop["@host"] ? '\n(' + hop["@host"] + ')' : '')
                let tmpLink = new GraphLink(lastHop, targetName)
                tmpLink.setColor("DodgerBlue")
                tmpLink.setWidth(Math.min(GraphHelper.normalize(this.averageRtt.min, this.averageRtt.max, hop["@rtt"]) * 2, 10))

                // if it does not link to itself
                if (tmpLink.source != tmpLink.target) {
                    this.linkList.push(tmpLink)
                }

                this.addNodesFoundInTraces(targetName)
                lastHop = targetName
            });
        } else {
            // add no traceroute information link
            let noTracerouteLink = new GraphLink("localhost", hostNameIp)
            noTracerouteLink.setColor("black")
            noTracerouteLink.setLineType("dashed")

            this.linkList.push(noTracerouteLink)
        }
    }

    static normalize(min: number, max: number, value: number) {
        // zi = (xi – min(x)) / (max(x) – min(x))
        return (value - min) / (max - min)
    }

    static getMaxMinRtt(nmaprun: any): AverageRtt {
        let max = -1
        let min = -1
        nmaprun.host.forEach((host: any) => {
            if (Array.isArray(host.trace?.hop)) {
                host.trace?.hop.forEach((hop: any) => {
                    if (max < hop["@rtt"]) {
                        max = hop["@rtt"]
                    }
                    if (min > hop["@rtt"]) {
                        min = hop["@rtt"]
                    }
                }
                )
            } else {
                if (max < host.trace?.hop["@rtt"]) {
                    max = host.trace?.hop["@rtt"]
                }
                if (min > host.trace?.hop["@rtt"]) {
                    min = host.trace?.hop["@rtt"]
                }
            }
        });
        return { min, max }
    }

    static getNodeColorOnPorts(host: any): string {
        if (host.ports == null) {
            return "gray"
        } else if (host.ports?.port?.length >= 3 && host.ports.port?.length <= 6) {
            return "yellow"
        } else if (host.ports?.port?.length > 6) {
            return "red"
        } else if (host.ports?.port?.length < 3 || host.ports?.port || host.ports?.extraports) { // if no array
            return "greenyellow"
        } else {
            // unkown (error)
            return "lightgray"
        }
    }
}
