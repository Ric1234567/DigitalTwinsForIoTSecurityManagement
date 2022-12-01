import time

import app


def evaluate_complete_network_scan():
    stat = []
    for i in range(10):
        start = time.time()
        app.get_full_network_report('-sS -T4 -F --traceroute 192.168.178.*')
        duration = time.time() - start
        stat.append(duration)
        print('Duration ' + str(duration))
        time.sleep(3)

    average = sum(stat) / len(stat)
    print('Average ' + str(average))
