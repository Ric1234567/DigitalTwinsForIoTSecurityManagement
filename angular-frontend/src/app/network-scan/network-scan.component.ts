import { Component, OnInit } from '@angular/core';
import * as echarts from 'echarts';
import { EChartsCoreOption } from 'echarts';
import { Util } from 'src/app/util';
import GraphHelper from 'src/models/graphHelper';
import { HostInformation } from 'src/models/hostInformation';

@Component({
  selector: 'app-network-scan',
  templateUrl: './network-scan.component.html',
  styleUrls: ['./network-scan.component.css']
})
export class NetworkScanComponent implements OnInit {

  nmapCustomCommandSuffix = "-sS -T4 -F 192.168.178.* --traceroute";

  networkgraphDOM!: HTMLElement;
  networkGraph!: echarts.ECharts;
  loadingScan: boolean = false;
  networkScan: any;

  hostInformation!: HostInformation;

  constructor() { }


  ngOnInit(): void {
    this.networkgraphDOM = document.getElementById("networkgraph")! as HTMLElement
    this.networkGraph = echarts.init(this.networkgraphDOM)

    let options: EChartsCoreOption = {
      title: {
        text: "Network Topology"
      },
      tooltip: {},
      // animationDurationUpdate: 1000,
      animationEasingUpdate: "linear",
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
            layoutAnimation: false
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

    this.networkGraph.on('click', (params) => this.onClickGraph(params))

    this.networkGraph.setOption(options)

    this.getLastNetworkReport()
  }

  async onClickExecuteCustomNetworkScan() {
    let nmapCustomNetworkScan = await this.fetchNetworkScan('GET', 'custom_network_scan/' + this.nmapCustomCommandSuffix) as any
    this.networkScan = nmapCustomNetworkScan

    this.setNetworkReport(nmapCustomNetworkScan.nmaprun)
  }

  async onClickEndlessNetworkScan() {
    let delay = 30
    let util = new Util
    let route = 'start/endless_network_scan?delay=' + delay
    try {
      let resp = await util.fetchFromBackend('GET', route) as any
    } catch (error) {
      
    }
    console.log('hi');

    //let that:any = this
    setInterval(() => {
      console.log("refresh");
      this.getLastNetworkReport()
    }, delay * 1000);
  }

  private onClickGraph(params: any) {
    if (params.dataType == 'node') {
      console.log((params.name));

      for (const host of this.networkScan.nmaprun.host) {
        let hostIp = ""
        if (Array.isArray(host.address)) {
          hostIp = host.address[0]["@addr"]
        } else {
          hostIp = host.address["@addr"]
        }

        let hostNameIp = hostIp + (host.hostnames?.hostname["@name"] ? '\n(' + host.hostnames?.hostname["@name"] + ')' : '')
        if (hostNameIp == params.name) {
          this.hostInformation = new HostInformation(host)
        }
      }
    } else if (params.dataType == 'edge') {
      // todo
    }
  }

  async getLastNetworkReport() {
    let lastReport = await this.fetchNetworkScan('GET', 'last_network_scan') as any
    this.networkScan = lastReport

    this.setNetworkReport(lastReport.nmaprun)
  }

  async onClickGetNetworkReport() {
    let nmapNetworkScan = await this.fetchNetworkScan('GET', 'network_scan') as any

    this.networkScan = nmapNetworkScan

    this.setNetworkReport(nmapNetworkScan.nmaprun)
  }

  private async fetchNetworkScan(method: string, route: string) {
    let networkScanReport
    try {
      let util = new Util
      this.loadingScan = true
      networkScanReport = await util.fetchFromBackend(method, route) as any
    } catch (error: any) {
      alert(error.message)
      return
    } finally {
      this.loadingScan = false
    }

    return networkScanReport
  }

  private setNetworkReport(nmapRun: any) {
    // check if hosts found
    if (nmapRun.host == null) {
      console.log("No hosts found!");

      return
    }

    this.hostInformation = new HostInformation(nmapRun.host[0])

    // graph
    let graphHelper: GraphHelper = new GraphHelper()
    let graphContent = graphHelper.getGraphContent(nmapRun)

    this.networkGraph.setOption({
      series: {
        data: graphContent.nodeList,
        links: graphContent.linkList
      }
    })
    // console.log(this.networkGraph.getOption()["series"])
  }

}
