import { Component, OnInit } from '@angular/core';
import { Host } from 'src/models/host';
import { SshInformation } from 'src/models/sshInformation';
import { Util } from '../util';

@Component({
  selector: 'app-analysis',
  templateUrl: './analysis.component.html',
  styleUrls: ['./analysis.component.css']
})
export class AnalysisComponent implements OnInit {

  loading: boolean = false

  isRefreshing: boolean = false
  refreshIntervalId: any

  analysisResult: any = []
  ipHosts: Host[] = []
  selectedHost: Host = this.ipHosts[0]

  constructor() { }

  ngOnInit(): void {
    this.getSshHosts()
  }

  private async getSshHosts() {
    this.loading = true
    let util = new Util()
    let response = await util.fetchFromBackend('GET', 'ip_hosts')
    this.loading = false

    this.ipHosts = response
  }

  async getAnalysisResult() {
    if (!this.selectedHost) {
      alert('Select host first!')
      return
    }

    this.loading = true
    let util = new Util()
    let response = await util.fetchFromBackend('GET', 'analysis/' + this.selectedHost.ip)
    this.loading = false

    if (response.response){
      this.analysisResult = null
      return
    }

    this.analysisResult = response
  }

  async onClickFixHost(issue: any) {
    console.log(issue);

    let util = new Util()
    let response = await util.fetchFromBackend('GET', 'fix/' + issue.host_information.ip + "/" + issue.issue_type)

    alert(response.response)
  }

  onClickAnalyse(event: Event) {
    this.getAnalysisResult()
  }
}
