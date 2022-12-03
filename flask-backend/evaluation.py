from evaluations.IpPortEvaluation import evaluate_port
from evaluations.CompleteScanEvaluation import evaluate_complete_network_scan
from evaluations.MosquittoEvaluation import evaluate_mosquitto
from evaluations.OsqueryEvaluation import evaluate_osquery
from evaluations.Zigbee2MqttEvaluation import evaluate_zigbee2mqtt


# Evaluation of the processing time of the use cases.
if __name__ == '__main__':
    print('Complete Network Scan Evaluation #######################################################')
    evaluate_complete_network_scan('-sS -T4 -F --traceroute 192.168.178.*')
    print()

    print('IP-Port Evaluation #######################################################')
    evaluate_port('192.168.178.51')
    print()

    print('Osquery Evaluation #######################################################')
    evaluate_osquery('192.168.178.51', 22)
    print()

    print('Mosquitto Evaluation #######################################################')
    evaluate_mosquitto('192.168.178.51', 22)
    print()

    print('Zigbee2Mqtt Evaluation #######################################################')
    evaluate_zigbee2mqtt('192.168.178.51', 22)
    print()

