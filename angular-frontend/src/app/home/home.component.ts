import { Component, OnInit } from '@angular/core';
import Constants from '../constants';
import { Util } from '../util';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  availableServices: any = []
  selectedStartService: string = ''
  serviceStartRequestParameter: string = '?delay=60'

  runningServices: any = []

  isRefreshing: boolean = false
  loadingRefresh: boolean = false

  refreshIntervalId: any

  constructor() { }

  ngOnInit(): void {
    this.getRunningServices()
    this.startRefreshInterval()
    this.getAvailableServices()
  }

  private startRefreshInterval() {
    this.isRefreshing = true
    console.log('auto-refresh started');

    this.refreshIntervalId = setInterval(() => {
      this.getRunningServices()
      this.getAvailableServices()
    }, 3000);
  }

  async getRunningServices() {
    let util = new Util
    let response = await util.fetchFromBackend('GET', 'running_services') as any

    this.runningServices = response.response
  }

  async getAvailableServices() {
    let util = new Util
    let response = await util.fetchFromBackend('GET', 'available_services') as any

    this.availableServices = response.response
  }

  async stopService(element: any) {
    let util = new Util
    // stop with pid
    let response = await util.fetchFromBackend('GET', 'stop/' + element.pid) as any
    console.log(response.response);

    this.getRunningServices()
  }

  onChangeAutoRefresh(event: any) {
    if (this.isRefreshing) {
      this.startRefreshInterval()
    } else {
      console.log('auto-refresh stopped');

      clearInterval(this.refreshIntervalId)
    }
  }

  async onClickStartService(event: any) {
    if (this.selectedStartService) {
      let util = new Util
      try {
        let response = await util.fetchFromBackend('GET', 'start/' + this.selectedStartService + this.serviceStartRequestParameter) as any
        alert(response.response)
      } catch (error) {
        alert(error)
      }
    } else {
      alert('Select service first!')
    }
  }
}
