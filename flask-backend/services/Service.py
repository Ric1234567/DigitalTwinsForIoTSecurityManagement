import string
from multiprocessing import Process


class Service:
    def __init__(self, name: string, description: string, args: tuple, process: Process):
        self.name: string = name
        self.description: string = description
        self.args: tuple = args
        self.process: Process = process

    def start(self):
        self.process.start()

    def stop(self):
        self.process.terminate()

    def repr_json(self):
        return dict(name=self.name,
                    description=self.description,
                    args=self.args,
                    pid=self.process.pid,
                    isalive=self.process.is_alive())
