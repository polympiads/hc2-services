
import threading
import time
from typing import Callable

import printout.task
import logging

logger = logging.getLogger("hc2admin.tasks")

class TaskThread(threading.Thread):
    time: float    = 60
    func: Callable = lambda : None
    __stop: bool   = False
    
    __threads = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TaskThread.__threads.append(self)
    @staticmethod
    def join_all ():
        for thread in TaskThread.__threads:
            thread.join()
    
    def join(self, timeout = None):
        self.__stop = True
        super().join(timeout)

    def run(self):
        while not self.__stop:
            self.func()

            time.sleep(self.time)

def run_task_thread (func: Callable, duration: "float | None" = None):
    thread = TaskThread()
    thread.daemon = True
    thread.func   = func

    if duration is not None:
        thread.time = duration

    thread.start()
def run_tasks ():
    logger.info("Starting all tasks thread.")
    run_task_thread(printout.task.printout_query_task)
