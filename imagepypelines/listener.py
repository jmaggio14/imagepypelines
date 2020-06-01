import socket, sys, queue, threading, time, signal, random

# WARNING: temporary - remove this once it's added to the module
from imagepypelines import get_logger


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8000
# We're going to need one of these per pipeline instance!!!
THREAD_QUEUE = queue.Queue()


###############################################################################
def handler(signum, frame):
    LISTENER.stop_thread()
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

    if i == 0:
        raise RuntimeError

    print("something %s" % i)

###############################################################################
def spawn_client_threads(n):
    threads = [threading.Thread(target=clint, args=(i,), name="Clint")
               for i in range(n)]

    for t in threads:
        t.start()

###############################################################################
class Listener(threading.Thread):
    def __init__(self, host, port, *args, **kwargs):
        kwargs['name'] = "Listener"
        super().__init__(*args, **kwargs)

        # build the listener socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #<-- UDP SOCKET
        self.sock.setblocking(0) #<-- Async, no wait
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #<-- Reuse same addr
        self.sock.bind( (host, port) )

        # auto close the thread in an exit condition
        self.daemon = True
        # create a logger
        self.logger = get_logger('Listener')
        # auto start the thread
        self.start()

    ############################################################################
    def run(self):
        t = threading.currentThread()
        # NOTE: Add way to communicate to main thread in a critical error
        while getattr(t, "running", True):
            try:
                out = self.sock.recv(2048)
                # NOTE: have a separate queue for every pipeline
                THREAD_QUEUE.put(out.decode())
            except BlockingIOError:
                print("error")
            time.sleep(1)
        self.sock.close()

    # __ Thread Killer _______________________________________________________
    def stop_thread(self):
        self.logger.warning("Closing Thread " + self.name)
        self.running = False
        # t = threading.currentThread()
        # setattr(t, 'running', False)  # t.running = False
        old_t = time.monotonic()
        self.join()
        time2join = time.monotonic() - old_t
        self.logger.warning(f"{self.name} Dead, took {time2join}s to die")


class Emitter(threading.Thread):



LISTENER = Listener(DEFAULT_HOST, DEFAULT_PORT)


if __name__ =="__main__":
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handler)

    spawn_client_threads(3)
    print("number of active threads:", threading.active_count())

    while True:
        if not THREAD_QUEUE.empty():
            print( THREAD_QUEUE.get() )
            time.sleep(0.5)
