import { Component } from '@angular/core';
import { Util } from './util';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  title = 'angular-frontend';

  // test get von backend
  async test() {
    console.log('get')

    let util = new Util
    let result = await util.fetchFromBackend('GET', 'listening_ports')
    console.log(result)
  }
}
