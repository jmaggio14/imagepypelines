# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2020 Jeff Maggio, Ryan Hartzell, and collaborators
#
import socket, sys, queue, threading, time, signal, random

# WARNING: temporary - remove this once it's added to the module
from imagepypelines import get_logger


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8000
# We're going to need one of these per pipeline instance!!!
THREAD_QUEUE = queue.Queue()
MANAGER = None

###############################################################################
def handler(signum, frame):
    print(f"frame = {frame}")
    MANAGER.stop_thread()
    print(threading.active_count())
    print(f"ERROR: Program closed due to {signal.Signals(signum).name}")
    sys.exit(1)

###############################################################################
def clint(i):
    c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #<-- UDP SOCKET
    c.connect((DEFAULT_HOST,DEFAULT_PORT))
    time.sleep(random.randint(1,5))
    c.send( bytes(f"Hello {i} \r", 'utf-8') )
    c.close()

    print("something %s" % i)

###############################################################################
def spawn_client_threads(n):
    threads = [threading.Thread(target=clint, args=(i,), name="Clint")
               for i in range(n)]

    for t in threads:
        t.start()

###############################################################################
class BaseCommThread(threading.Thread):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)
        # auto close the thread in an exit condition
        # self.daemon = True
        # create a logger
        self.logger = get_logger(self.name)

    # ____ Thread Killer _____________________________________________________
    def stop_thread(self):
        self.logger.warning("Closing Thread " + self.name)
        self.running = False
        # t = threading.currentThread()
        # setattr(t, 'running', False)  # t.running = False
        old_t = time.monotonic()
        self.join()
        time2join = time.monotonic() - old_t
        self.logger.warning(f"{self.name} Dead, took {time2join}s to die")

###############################################################################
class Listener(BaseCommThread):
    def __init__(self, host, port):
        # build the listener socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #<-- UDP SOCKET
        self.sock.setblocking(0) #<-- Async, no wait
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #<-- Reuse same addr
        self.sock.bind( (host, port) )
        self.t = None

        super().__init__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"exc_type = {exc_type}\n")
        print(f"exc_value = {exc_value}\n")
        print(f"traceback = {traceback}\n")
        self.stop_thread()

    ############################################################################
    def run(self):
        self.t = threading.currentThread()
        # NOTE: Add way to communicate to main thread in a critical error
        while getattr(self.t, "running", True):
            try:
                out = self.sock.recv(2048)
                # NOTE: have a separate queue for every pipeline
                THREAD_QUEUE.put(self.name + out.decode())
            except BlockingIOError:
                print("error")
            time.sleep(1)
        self.sock.close()

###############################################################################
class Manager(BaseCommThread):
    def __init__(self):
        # assigned in run_listener_forever()
        self.listener = None
        super().__init__()
        self.start()

    def run(self):
        t = threading.currentThread()
        while getattr(t, "running", True):
            i = 0
            with Listener(DEFAULT_HOST, DEFAULT_PORT) as l:
                self.listener = l
                i += 1
                self.logger.info(f"Starting new Listener thread '{l.name}{i}'")
                self.listener.start()
                while getattr(self.listener.t, "running", True):
                    pass

        self.stop_thread()

    def stop_thread(self):
        if self.listener.is_alive():
            self.listener.stop_thread()
        print(f"self.listener.is_alive() = {self.listener.is_alive()}")
        super().stop_thread()

MANAGER = Manager()

if __name__ =="__main__":
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handler)

    spawn_client_threads(3)
    print("number of active threads:", threading.active_count())

    while True:
        print("mainloop")
        time.sleep(0.5)
        if not THREAD_QUEUE.empty():
            print( THREAD_QUEUE.get() )
            time.sleep(0.5)
