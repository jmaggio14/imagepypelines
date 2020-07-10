import socket, time
from collections import namedtuple

def sockspeak(msg):
    if type(msg) is str:
        msg = msg.encode()
    return msg

def normalspeak(msg):
    if type(msg) is bytes:
        msg = msg.decode()
    return msg.rstrip()

def create_non_blocking_udp_client(host, port):
    c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #<-- UDP SOCKET
    c.setblocking(0)
    c.connect((host,port))
    return c

def create_non_blocking_udp_server(host, port):
    c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # <-- UDP SOCKET
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # <-- Reuse addr
    c.bind((host,port))  # <-- bind socket server to host & port
    c.setblocking(0)
    return c

def create_non_blocking_tcp_client(host, port):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #<-- UDP SOCKET
    c.connect((host,port))
    c.setblocking(0)
    return c

def create_non_blocking_tcp_server(host, port):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # <-- UDP SOCKET
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # <-- Reuse addr
    c.setblocking(0)
    c.bind((host,port))  # <-- bind socket server to host & port
    c.listen(10)  # <-- max of 10 unaccepted connections before not accepting anymore
    return c


# [JEFF] I am probably going to move this into a more generic core/ file,
#        any suggestions?
# __ Event/Method Queueing Class _____________________________________________
class EventQueue:
    '''
    This Class is meant to be a simple task scheduler that runs tasks in any
    of the following ways:
        * Immediately
        * After a delay (seconds)
        * After a delay & repeatedly every specified interval of time (seconds)
    '''
    ScheduledEvent = namedtuple('ScheduleEvent', ['event_time', 'task'])

    def __init__(self):
        self.events = []

    def run_scheduled_tasks(self):
        ''' Runs all tasks that are scheduled to run at the current time '''
        t = time.monotonic()
        while self.events and self.events[0].event_time <= time.monotonic():
            event = heappop(self.events)
            event.task()

    def add_task(self, event_time, task):
        'Helper function to schedule one-time tasks at specific time'
        heappush(self.events, EventQueue.ScheduledEvent(event_time, task))

    def call_later(self, delay, task):
        'Helper function to schedule one-time tasks after a given delay'
        self.add_task(time.monotonic() + delay, task)

    def call_periodic(self, delay, interval, task):
        'Helper function to schedule recurring tasks'
        def inner():
            task()
            self.call_later(interval, inner)
        self.call_later(delay, inner)
