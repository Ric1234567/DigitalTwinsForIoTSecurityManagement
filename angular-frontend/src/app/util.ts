export class Util {
    async fetchFromBackend(method: string, route: string) {
        try {
            const response = await fetch('http://localhost:5000/' + route, {
                method: method,
                headers: {
                    Accept: 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error! status: ${response.status}`);
            }

            const result = await response.json();
            //console.log(JSON.stringify(result, null, 4));
            return result
        } catch (error: any) {
            console.error(error)
        }
    }
}