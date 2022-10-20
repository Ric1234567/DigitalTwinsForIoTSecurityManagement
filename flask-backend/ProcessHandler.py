#!/usr/bin/python3
import time
from multiprocessing import active_children, current_process

from NmapHandler import NmapHandler


def get_processes():
    return active_children()


def get_process_by_name(name):
    processes = active_children()
    for process in processes:
        if process.name == name:
            return process
    # no match
    return None


def endless_network_scan(nmap_command, delay):
    while True:
        print("Performing Network Scan (" + nmap_command + "," + current_process().name + "," + str(delay) + ")")
        nmap_handler = NmapHandler()
        nmap_handler.scan_network(nmap_command)
        time.sleep(delay)
