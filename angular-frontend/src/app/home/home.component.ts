import { Component, OnInit } from '@angular/core';
import Constants from '../constants';
import { Util } from '../util';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  services: any = []
  isRefreshing: boolean = false
  loadingRefresh: boolean = false

  refreshIntervalId: any

  constructor() { }

  ngOnInit(): void {
    this.getRunningServices()
    this.startRefreshInterval()
  }

  private startRefreshInterval() {
      this.isRefreshing = true
      console.log('auto-refresh started');
      
      this.refreshIntervalId = setInterval(() => {
        this.getRunningServices()
      }, 3000);
  }

  async getRunningServices() {
    let util = new Util
    let response = await util.fetchFromBackend('GET', 'running_services') as any

    this.services = response.response
  }

  async stopService(element: any) {
    let util = new Util
    // stop with pid
    let response = await util.fetchFromBackend('GET', 'stop/' + element.pid) as any

    this.getRunningServices()
  }

  onChangeAutoRefresh(event:any) {
    if (this.isRefreshing) {
      this.startRefreshInterval()
    } else {
      console.log('auto-refresh stopped');

      clearInterval(this.refreshIntervalId)
    }
  }

}
