import { Component, OnInit } from '@angular/core';
import { Util } from '../util';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  services: any = []
  isRefreshing: boolean = false

  constructor() { }

  ngOnInit(): void {
    this.getAllServices()
    this.startRefreshInterval()
  }

  private startRefreshInterval() {
    if (!this.isRefreshing) {
      this.isRefreshing = true
      setInterval(() => {
        console.log("refresh");
        this.getAllServices()
      }, 3000);
    }
  }

  async getAllServices() {
    let runningServices = await this.getRunningServices()
    let availableServices = await this.getServices()

    this.services = runningServices

    for (const availableService of availableServices) {
      if (this.services.filter((s: any) => s.name === availableService).length > 0) {
        continue
      }
      this.services.push({
        'pid': null,
        'name': availableService,
        'isalive': false
      })
    }
  }

  async getServices() {
    let util = new Util
    let response = await util.fetchFromBackend('GET', 'services') as any

    return response.response
  }

  async getRunningServices() {
    let util = new Util
    let response = await util.fetchFromBackend('GET', 'running_services') as any

    return response.response
  }

  async stopService(element: any) {
    let util = new Util
    let response = await util.fetchFromBackend('GET', 'stop/' + element.name) as any

    this.getAllServices()
  }

  async startService(element: any) {
    let util = new Util
    let delay = 60
    let response = await util.fetchFromBackend('GET', 'start/' + element.name + '?delay=' + delay) as any

    this.getAllServices()
  }

  async onClickStartStopService(element: any) {
    if (element.isalive) {
      await this.stopService(element)
    } else {
      await this.startService(element)
    }
  }
}
