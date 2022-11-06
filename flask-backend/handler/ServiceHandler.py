#!/usr/bin/python3
import numbers
import string
import time
from multiprocessing import active_children, current_process, Process

from handler.SubnetworkHandler import SubnetworkHandler
import constants
from handler.DatabaseHandler import DatabaseHandler
from handler.NmapHandler import NmapHandler
from handler.ssh.SshHandler import SshHandler

process_dict = {}


def get_processes():
    return active_children()


def get_process_by_name(name):
    processes = active_children()
    for process in processes:
        if process.name == name:
            return process
    # no match
    return None


def start_service(process_name: string, target, args: tuple):
    service_process = Process(name=process_name,
                              target=target,
                              args=args)
    service_process.start()
    process_dict[service_process.pid] = service_process
    print("Start service: " + service_process.name)
    return service_process









