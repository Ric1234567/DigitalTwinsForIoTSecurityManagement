import { Component, OnInit } from '@angular/core';
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

  constructor() { }

  ngOnInit(): void {
    //this.startRefreshInterval()
    this.getAnalysisResult()
  }

  onChangeAutoRefresh(event: any) {
    if (this.isRefreshing) {
      this.startRefreshInterval()
    } else {
      console.log('auto-refresh stopped');

      clearInterval(this.refreshIntervalId)
    }
  }

  private startRefreshInterval() {
    if(!this.isRefreshing) {
      this.isRefreshing = true
      console.log('auto-refresh started');
  
      this.refreshIntervalId = setInterval(() => {
        console.log('refresh');
        
        this.getAnalysisResult()
      }, 3000);
    }
  }

  async getAnalysisResult() {
    this.loading = true

    // todo make dynamic
    const ip = '192.168.178.51'

    let util = new Util()
    let response = await util.fetchFromBackend('GET', 'analysis/' + ip)
    this.loading = false

    this.analysisResult = response
  }

  async onClickFixHost(issue: any) {
    console.log(issue);
    
    let util = new Util()
    let response = await util.fetchFromBackend('GET', 'fix/' + issue.host_ip + "/" + issue.issue_type)
    
    alert(response.response)
  }
}
