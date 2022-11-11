import { Component, OnInit } from '@angular/core';
import { NetworkConfiguration } from 'src/models/networkConfiguration';
import { Util } from '../util';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css']
})
export class ConfigurationComponent implements OnInit {

  configuration?:NetworkConfiguration

  constructor() { }

  async ngOnInit() {
    this.getConfiguration()
  }

  async onClickSubmitConfiguration() {
    // send changes to server
    let util = new Util
    let response = await util.postToBackend('network_configuration', this.configuration)

    alert(response.response)
  }

  async getConfiguration() {
    let util = new Util
    let configurationResponse = await util.fetchFromBackend('GET', 'network_configuration')

    this.configuration = configurationResponse as NetworkConfiguration
    console.log(configurationResponse);
  }
}
