import { Component } from '@angular/core';

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

    try{
    const response = await fetch('http://localhost:5000/ping', {
    method: 'GET',
    headers: {
      Accept: 'application/json'
    }
  });

    if (!response.ok) {
      throw new Error(`Error! status: ${response.status}`);
    }
    const result = (await response.json());

    console.log(JSON.stringify(result, null, 4));
  } catch (error: any) {
    console.error(error)
  }
} 
}
