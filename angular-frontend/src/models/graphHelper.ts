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


    getGraphContent(nmaprun: any): GraphContent {
        this.averageRtt = GraphHelper.getMaxMinRtt(nmaprun)

        nmaprun.host.forEach((host: any) => {
            let hostIp = ""
            if (Array.isArray(host.address)) {
                hostIp = host.address[0]["@addr"]
            } else {
                hostIp = host.address["@addr"]
            }

            let hostNameIp = hostIp + (host.hostnames?.hostname["@name"] ? '\n(' + host.hostnames?.hostname["@name"] + ')' : '')

            // color / open ports
            let nodeColor = GraphHelper.getNodeColorOnPorts(host)

            let tmpNode: GraphNode = new GraphNode(hostNameIp, nodeColor)
            this.nodeList.push(tmpNode)

            // links / traces / hops
            this.getTraces(host, hostNameIp)
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
                tmpLink.setColor("#0096FF")
                tmpLink.setWidth(Math.min(GraphHelper.normalize(this.averageRtt.min, this.averageRtt.max, hop["@rtt"]) * 2, 10))

                // links to itself
                if (tmpLink.source != tmpLink.target) {
                    this.linkList.push(tmpLink)
                }

                this.addNodesFoundInTraces(targetName)
                lastHop = targetName
            });
        } else {
            // add no traceroute information link
            let noTracerouteLink = new GraphLink("localhost", hostNameIp)
            noTracerouteLink.setColor("#0096FF")
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
        if (host.ports.port?.length > 0 && host.ports.port?.length <= 3) {
            return "#00ff00"
        } else if (host.ports.port?.length > 3 && host.ports.port?.length <= 6) {
            return "#ff8800"
        } else if (host.ports.port?.length > 6) {
            return "#FF0000"
        }
        return "#b5b5b5"
    }
}
