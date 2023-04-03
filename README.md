# Digital Twins for IoT Security Management - Prototype
Prototype python implementation of the paper "Digital Twins for IoT Security Management". 
This prototype leverages the advantages of digital twins for Internet of Things network management.
It uses several libraries to enable network monitoring and management even for hidden controllable IoT devices not detected by IP network scans.

## Software
### Raspberry Pi
| Software					| Version 	|
| ----------------- 		| --------- |
| Raspberry Pi OS (64-Bit)	| 11		|
| Docker					| 20.10.21	|
| Zigbee2Mqtt				| 1.28.2	|
| Eclipse-Mosquitto 		| 2.0.15	|
| Osquery (Daemon) 			| 5.5.1		|

### Server
| Software					| Version 	|
| ----------------- 		| --------- |
| Python					| 3.8.8		|
| Flask						| 1.1.2		|
| Nmap						| 7.93		|
| Angular					| 14.2.6	|
| Docker Desktop			| 4.13.0	|
| MongoDB					| 6.0.2		|

## Libraries
### Python
- [xmltodict](https://pypi.org/project/xmltodict/0.13.0/): Converting xml files to python dicts.
- [PyYAML](https://pypi.org/project/PyYAML/6.0/): YAML data serialization.
- [Flask](https://pypi.org/project/Flask/2.2.2/): Web server.
- [Flask-PyMongo](https://pypi.org/project/Flask-PyMongo/2.3.0/): MongoDB support for Flask applications.
- [Flask-Cors](https://pypi.org/project/Flask-Cors/3.0.10/): Cross Origin Resource Sharing (CORS) handling.
- [paramiko](https://pypi.org/project/paramiko/2.11.0/): SSH-Client.
- [python-libnmap](https://pypi.org/project/python-libnmap/0.7.3/): Nmap processing.

### JavaScript
| Library			| Version	|
| ----------------- | --------- |
| Angular CLI 		| 14.2.6 	|
| Node 				| 18.11.0	|
| npm				| 8.19.2	|
| rxjs				| 7.5.7		|
| typescript		| 4.7.4		|
| echarts			| 5.1.1		|
| ngx-echarts		| 14.0.0	|
| ngx-json-viewer	| 3.1.0		|
| tslib				| 2.3.0		|
| zone.js			| 0.11.4	|


## Installation

### Backend
- See the [requirements.txt](flask-backend/requirements.txt) file for the python package requirements.
- Nmap needs to be installed on your local machine. See the [offical installation guide of nmap](https://nmap.org/book/inst-windows.html). The Nmap directory needs to added to your command execution path!

### Frontend
- Node.js (npm)
- Angular 14.2.6

### Database
- Monogodb database running in an docker container. Setup: [docker-compose](docker-compose.yml)
