import { Component, OnInit } from '@angular/core';
import { Util } from './util';
import * as echarts from 'echarts';
import { EChartsCoreOption, EChartsOption } from 'echarts';
import GraphNode from 'src/models/graphNode';
import GraphLink from 'src/models/graphLink';
import GraphHelper from 'src/models/graphHelper';

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
    this.networkGraph.setOption(options)

    this.getLastNetworkReport()
  }

  async getLastNetworkReport() {
    let util = new Util
    this.loadingScan = true
    let lastReport = await util.fetchFromBackend('GET', 'last_network_scan') as any
    console.log(lastReport)
    this.loadingScan = false

    this.setNetworkReport(lastReport.nmaprun)
  }

  async onClickGetNetworkReport() {
    let util = new Util
    this.loadingScan = true
    let nmapNetworkScan = await util.fetchFromBackend('GET', 'network_scan') as any
    console.log(nmapNetworkScan)
    this.loadingScan = false

    this.setNetworkReport(nmapNetworkScan.nmaprun)
  }

  setNetworkReport(nmapRun: any) {
    let graphHelper: GraphHelper = new GraphHelper()
    let graphContent = graphHelper.getGraphContent(nmapRun)

    // this.networkScan = nodeList

    this.networkGraph.setOption({
      series: {
        data: graphContent.nodeList,
        links: graphContent.linkList
      }
    })
    // console.log(this.networkGraph.getOption()["series"])
  }




}
