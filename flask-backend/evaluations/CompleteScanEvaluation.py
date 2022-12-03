import string
import time

import app


# Evaluation of the complete network scan.
def evaluate_complete_network_scan(command: string):
    stat = []
    for i in range(10):
        start = time.time()
        app.get_full_network_report(command)
        duration = time.time() - start
        stat.append(duration)
        print('Duration ' + str(duration))
        time.sleep(3)

    average = sum(stat) / len(stat)
    print('Average ' + str(average))
