import { Component, OnInit } from '@angular/core';
import { Util } from './util';
import * as echarts from 'echarts';
import { EChartsCoreOption, EChartsOption } from 'echarts';
import GraphNode from 'src/models/graphNode';
import GraphLink from 'src/models/graphLink';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent implements OnInit {

  networkgraphDOM!: HTMLElement;
  networkGraph!: echarts.ECharts;
  loadingScan: boolean = false;

  title = 'angular-frontend';
  // networkScan: string = '';

  ngOnInit(): void {
    this.networkgraphDOM = document.getElementById("networkgraph")! as HTMLElement
    this.networkGraph = echarts.init(this.networkgraphDOM)

    let options: EChartsCoreOption = {
      title: {
        text: "Network"
      },
      tooltip: {},
      animationDurationUpdate: 3000,
      animationEasingUpdate: "quinticInOut",
      draggable: true,

      series: [
        {
          type: "graph",
          chartDataZoom: true,
          layout: "force",
          symbolSize: 20,
          roam: true, // mouse moving

          label: {
            position: "bottom"
          },
          draggable: false,
          force: {
            repulsion: 1500,
            gravity: 0.2,
            friction: 0.6,
            layoutAnimation: true
          },
          animation: false,

          edgeSymbol: ["none", "none"],
          edgeSymbolSize: [4, 10],
          edgeLabel: {
            fontSize: 20
          },
          // data: this.networkScan,
          // links: [],
          lineStyle: {
            opacity: 1,
            // width: 1,
            curveness: 0
          }
        }
      ]
    };
    this.networkGraph.setOption(options)

    this.getLastNetworkReport()
  }

  async getLastNetworkReport() {
    let util = new Util
    this.loadingScan = true
    let lastReport = await util.fetchFromBackend('GET', 'last_network_scan')
    console.log(lastReport)
    this.loadingScan = false

    this.setNetworkReport(lastReport)
  }

  async onClickGetNetworkReport() {
    let util = new Util
    this.loadingScan = true
    let nmapNetworkScan = await util.fetchFromBackend('GET', 'network_scan')
    console.log(nmapNetworkScan)
    this.loadingScan = false

    this.setNetworkReport(nmapNetworkScan)
  }

  setNetworkReport(nmapNetworkScan: any) {
    let nodeList: GraphNode[] = []
    let linkList: any = []

    let { min, max } = this.getMaxMinRtt(nmapNetworkScan.nmaprun)

    nmapNetworkScan.nmaprun.host.forEach((host: any) => {
      let hostIp = ""
      if (Array.isArray(host.address)) {
        hostIp = host.address[0]["@addr"]
      } else {
        hostIp = host.address["@addr"]
      }

      let hostNameIp = hostIp + (host.hostnames?.hostname["@name"] ? '\n(' + host.hostnames?.hostname["@name"] + ')' : '')

      // color / open ports
      let nodeColor = "#b5b5b5"
      if (host.ports.port?.length > 0 && host.ports.port?.length <= 3) {
        nodeColor = "#00ff00"
      } else if (host.ports.port?.length > 3 && host.ports.port?.length <= 6) {
        nodeColor = "#ff8800"
      } else if (host.ports.port?.length > 6) {
        nodeColor = "#FF0000"
      }

      let tmpNode:GraphNode = new GraphNode(hostNameIp, nodeColor)
      nodeList.push(tmpNode)

      // links / traces / hops
      if (host.trace != null) {
        let targetName = ""
        let lastHop: string = "localhost"

        if (Array.isArray(host.trace.hop)) {
          host.trace.hop.forEach((hop: any) => {
            targetName = hop["@ipaddr"] + (hop["@host"] ? '\n(' + hop["@host"] + ')' : '')
            let tmpLink = new GraphLink(lastHop, targetName)
            tmpLink.setColor("#0096FF")
            tmpLink.setWidth(Math.min(this.normalize(min, max, hop["@rtt"]) * 2, 10))

            // links to itself
            if (tmpLink.source != tmpLink.target) {
              linkList.push(tmpLink)
            }

            this.addNodesFoundInTraces(nodeList, targetName)
            lastHop = targetName
          });
        } else {
          targetName = host.trace.hop["@ipaddr"] + (host.trace.hop["@host"] ? '\n(' + host.trace.hop["@host"] + ')' : '')
          let tmpLink = new GraphLink(lastHop, targetName)
          tmpLink.setColor("#0096FF")
          tmpLink.setWidth(Math.min(this.normalize(min, max, host.trace.hop["@rtt"]) * 2, 10))

          // links to itself
          if (tmpLink.source != tmpLink.target) {
            linkList.push(tmpLink)
          }

          this.addNodesFoundInTraces(nodeList, targetName)
          lastHop = targetName
        }

      } else {
        // add no traceroute information link
        let tmpLink = new GraphLink("localhost", hostNameIp)
        tmpLink.setColor("#0096FF")
        tmpLink.setLineType("dashed")

        linkList.push(tmpLink)
      }
    });
    let localhostNode = new GraphNode("localhost", "#000")
    nodeList.push(localhostNode)

    console.log(linkList.length);

    // this.networkScan = nodeList

    this.networkGraph.setOption({
      series: {
        data: nodeList,
        links: linkList
      }
    })
    console.log(this.networkGraph.getOption()["series"])
  }

  private getMaxMinRtt(nmaprun: any) {
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
    return { max, min }
  }

  private normalize(min: number, max: number, value: number) {
    // zi = (xi – min(x)) / (max(x) – min(x))
    return (value - min) / (max - min)
  }

  private addNodesFoundInTraces(nodeList: any, targetName: string) {
    var found = false;
    for (var i = 0; i < nodeList.length; i++) {
      if (nodeList[i].name == targetName) {
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
      nodeList.push(tmpNode)
    }
  }

}
