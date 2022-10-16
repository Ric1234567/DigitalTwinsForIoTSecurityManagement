import { Component, OnInit } from '@angular/core';
import { Util } from './util';
import * as echarts from 'echarts';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent implements OnInit {

  networkgraphDOM!: HTMLElement;
  networkgraph!: echarts.ECharts;
  options: any;

  title = 'angular-frontend';
  networkScan: string = '';

  ngOnInit(): void {
    this.networkgraphDOM = document.getElementById("networkgraph")! as HTMLElement
    this.networkgraph = echarts.init(this.networkgraphDOM)

    let data = [
      {
        name: "karan",

        label: {
          show: true
        },
        itemStyle: { color: "#000" }
      },
      {
        name: "max",

        label: {
          show: true
        },
        itemStyle: { color: "#45128C" }
      },
      {
        name: "1800",

        label: {
          show: true
        },
        itemStyle: { color: "#45128C" }
      },
      {
        name: "manish",

        label: {
          show: true
        },
        itemStyle: { color: "#45128C" }
      },
      {
        name: "alan",

        label: {
          show: true
        },
        itemStyle: { color: "#45128C" }
      },
      {
        name: "amy",

        label: {
          show: true
        },
        itemStyle: { color: "#45128C" }
      },
      {
        name: "robert",

        label: {
          show: true
        },
        itemStyle: { color: "#d0d0d0" }
      }
    ];
    this.options = {
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
            position: "left"
          },
          draggable: false,
          force: {
            repulsion: 2000,
            gravity: 0.2
          },
          animation: true,

          edgeSymbol: ["circle", "arrow"],
          edgeSymbolSize: [4, 10],
          edgeLabel: {
            fontSize: 20
          },
          data: this.networkScan,
          links: [],
          /*links: [
            {
              source: "karan",
              target: "max",
              lineStyle: {
                color: "#A063EB"
              }
            },
            {
              source: "max",
              target: "robert",
              lineStyle: {
                color: "#A063EB"
              }
            },
            {
              source: "karan",
              target: "manish",
              lineStyle: {
                color: "#A063EB"
              }
            },
            {
              source: "manish",
              target: "alan",
              lineStyle: {
                color: "#A063EB"
              }
            },
            {
              source: "alan",
              target: "robert",
              lineStyle: {
                color: "#A063EB"
              }
            },

            {
              source: "karan",
              target: "manish",
              lineStyle: {
                color: "#A063EB"
              }
            },
            {
              source: "manish",
              target: "amy",
              lineStyle: {
                color: "#A063EB"
              }
            },
            {
              source: "amy",
              target: "robert",
              lineStyle: {
                color: "#A063EB"
              }
            }
          ],
          lineStyle: {
            opacity: 0.9,
            width: 2,
            curveness: 0
          }*/
        }
      ]
    };
  }


  async getNetworkReport() {
    let util = new Util
    let nmapNetworkScan = await util.fetchFromBackend('GET', 'network_scan')
    console.log(nmapNetworkScan)

    const node = {
      name: "name",

      label: {
        show: true
      },
      itemStyle: { color: "#000" }
    }

    let node_list: any = []
    nmapNetworkScan.nmaprun.host.forEach((host: any) => {
      //console.log(host.hostnames.hostname["@name"])
      let tmpNode = Object.assign({}, node)
      tmpNode.name = host.hostnames.hostname["@name"]
      node_list.push(tmpNode)
    });

    this.networkScan = node_list
    //this.options.series[0].data = node_list
    /*if(this.networkgraph == null){
      this.networkgraph = echarts.init(document.getElementById("networkgraph") as HTMLElement)
    }*/

    this.networkgraph.setOption({ series: { data: node_list } })
  }
}
