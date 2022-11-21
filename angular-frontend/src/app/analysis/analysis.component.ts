import { Component, OnInit } from '@angular/core';
import { Host } from 'src/models/host';
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

  analysisResult: any = null
  ipHosts: Host[] = []
  selectedHost: Host = this.ipHosts[0]
  emptyIssues: boolean = false

  constructor() { }

  async ngOnInit() {
    await this.getIpHosts()
    await this.getLatestAnalysis()
  }

  async getLatestAnalysis() {
    this.loading = true
    try {
      let util = new Util()
      var response = await util.fetchFromBackend('GET', 'latest_analysis_result')
    } catch (error: any) {
      alert(error.message)
      return
    } finally {
      this.loading = false
    }

    if (response.response) {
      this.analysisResult = null
      this.emptyIssues = true
      return
    }

    if (response?.security_issues.length == 0) {
      this.emptyIssues = true
    }
    else {
      this.emptyIssues = false
    }

    this.analysisResult = response
  }

  private async getIpHosts() {
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
    try {
      let util = new Util()
      var response = await util.fetchFromBackend('GET', 'analysis/' + this.selectedHost.ip)
    } catch (error: any) {
      alert(error.message)
      return
    } finally {
      this.loading = false
    }

    if (response.response) {
      this.analysisResult = null
      this.emptyIssues = true
      return
    }

    this.emptyIssues = false
    this.analysisResult = response
  }

  async onClickFixHost(issue: any) {
    console.log(issue);

    this.loading = true
    try {
      let util = new Util()
      var response = await util.fetchFromBackend('GET', 'fix/' + this.analysisResult.host_information.ip + "/" + issue.issue_type)
    } catch (error: any) {
      alert(error.message)
      return
    } finally {
      this.loading = false
    }

    alert(response.response)
  }

  onClickAnalyse(event: Event) {
    this.getAnalysisResult()
  }

  getTimestamp() {
    let util = new Util()
    return util.convertUnixTimeToDate(this.analysisResult.unixTime)
  }

  getHostInformation() {
    let result = ''
    if (this.analysisResult?.host_information?.ip) {
      result += this.analysisResult.host_information.ip
    }
    if (this.analysisResult?.host_information?.hostname) {
      result += ' (' + this.analysisResult.host_information.hostname + ')'
    }

    return result
  }
}
