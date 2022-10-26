export class Util {
    async fetchFromBackend(method: string, route: string): Promise<string> {
        const response = await fetch('http://localhost:5000/' + route, {
            method: method,
            headers: {
                Accept: 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error(`${response.status}! ${response.statusText}. ${await response.text()}`);
        }
        return await response.json();
    }

    async postToBackend(route: string, data: any): Promise<any> {
        const response = await fetch('http://localhost:5000/' + route, {
            method: 'POST',
            headers: {
                Accept: 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error(`${response.status}! ${response.statusText}. ${await response.text()}`);
        }
        return await response.json();
    }

    convertUnixTimeToDate(unixTimestamp: number) {
        let date = new Date(unixTimestamp * 1000);
        return date.toString()
    }
}