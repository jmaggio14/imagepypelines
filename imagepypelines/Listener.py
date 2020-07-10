import threading, logging, time, select, uuid, asyncio, socket
from random import randint
from heapq import heappush, heappop
from collections import namedtuple
from functools import partial
from queue import Queue
from struct import pack, unpack
from .core.socketing import (create_non_blocking_tcp_server,  # For DASHBOARD/LISTENER
                             create_non_blocking_tcp_client,  # For LISTENER/PIPE
                             EventQueue,  # For scheduling tasks
                             sockspeak, normalspeak)

#    v-------------------------
# [JEFF], read this first: <-----------------------------[JEFF!]
# I commented the BaseCommThread to be a bit easier to understand so it could
# possibly be used elsewhere, might wanna move this to its own core/ file as
# it is not directly related with socketing. There is also a way to induce an
# exception in the thread to kill it in an unsafe manner which I could add if
# you wanted but that's cringe bro.
#
# Additionally I commented out all the communication simulation code, perhaps
# it can be adapted for testing at some point unless you plan on making a
# simulated Pipeline, Session, & Dashboard object for testing as well.


# __ Global Variables ________________________________________________________
PipeSession = namedtuple("PipeSession", ["address", "sock", "id"])
DashSession = namedtuple("DashSession", ["address", "sock", "id"])

# __ Logger Initialization ___________________________________________________
# [JEFF] REPLACE THE DEFAULT LOGGER WITH YOUR FANCY ONE
logging.basicConfig(level=logging.DEBUG)


# __ Parent Thread Manager Class _____________________________________________
class BaseCommThread(threading.Thread):
    '''
    Parent Class to all thread manager classes.
    '''
    def __init__(self):
        super().__init__(name=self.__class__.__name__)
        self.daemon = True

    def __enter__(self):
        '''
        Starts the thread in its own context manager block.
        Note: If the running thread is meant to be run indefinitely it is not
              recommended to use it as a context manager as once you exit the
              context manager, the thread will safely shut down via the
              __exit__() method.
        '''
        self.run()

    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Is called once the context leaves the manager, safely signals the
        running thread to shutdown.
        '''
        self.stop_thread()

    # ____ Run Function ______________________________________________________
    def run(self):
        '''
        This function is to be overloaded in the child class. If the thread is
        to be run indefinitely (as in not for a fixed duration), you MUST
        structure this function as follows:

        --[START]--------------------------------------------------------------
        self.t = threading.current_thread()  # Grab current threading context
        ...
        while getattr(self.t, 'running', True):
            ...
        ...
        --[END]--------------------------------------------------------------

        This is necessary as the classes stop_thread() method can safely shut
        down the running thread by changing self.running to False, thus
        invalidating the while loop's condition.
        '''
        pass

    # ____ Thread Killer _____________________________(Kills with kindness)___
    def stop_thread(self):
        '''
        This is a convenience function used to safely end the running thread.
        Note: This will only end the running thread if the run() function
              checks for the classes 'running' attribute (as demonstrated in
              the docstring of the run() function above).
              This only works if the running thread is not hanging, this will
              prevent the while loop from re-evaluating its condition
        '''
        logging.warning("Closing Thread " + self.name)
        self.running = False
        self.join()
        logging.warning(f"{self.name} has stopped")

# [JEFF] The commented section below is mean to simulate the Dashboard in its
#        own managed thread.
# # __ Dashboard Simulator Thread ______________________________________________
# class DashboardThread(BaseCommThread):
#
#     def __init__(self, addr):
#         super().__init__()
#         self.addr = addr
#         self.t = None
#
#     @staticmethod
#     def send_msg_to_listeners(sessions):
#         '''
#         Periodic task to simulate Billy sending data from DASHBOARD to
#         the LISTENER.
#         '''
#         for c in sessions:
#             if sessions[c]:  # If client & NOT the DASHBOARD socket server
#                 msg=f"{randint(1,10)*randint(1,10)}"
#                 logging.info(f"[DASHBOARD]: Sending '{msg}' to LISTENER at '{sessions[c].address}'")
#                 msg_b = sockspeak(msg)
#                 length = pack('>Q', len(msg_b))
#                 c.sendall(length)  # Dashboard -> Listener
#                 c.sendall(msg_b)  # Dashboard -> Listener
#
#     @staticmethod
#     def disconnect_client(sessions, c):
#         c.shutdown(socket.SHUT_RDWR)
#         c.close()
#         del sessions[c]
#
#     @staticmethod
#     def disconnect_all(sessions):
#         clients = [c for c in sessions if sessions[c]]
#         map(partial(DashboardThread.disconnect_client, sessions), clients)
#         for s in sessions.keys():  # Kill the Socket Server last
#             s.close()
#
#     @staticmethod
#     def recvall(c, length):
#         data = b''
#         while len(data) < length:
#             remaining = length - len(data)
#             data = c.recv(min(remaining, 4096))
#         return data
#
#     def connect(self, c, sessions):
#         c, a = c.accept()
#         logging.info(f"[DASHBOARD]: Accepting connection from {a}")
#         sessions[c] = PipeSession(a, c, uuid.uuid4())
#
#     def run(self):
#         self.t = threading.current_thread()  # Grab current threading context
#         # __ Dashboard Event Loop State Info _________________________________
#         s = create_non_blocking_tcp_server(*self.addr)
#         sessions = {}   # { csocket : PipeSession(address, file)}
#         events = EventQueue()  # Class that queues events
#         sessions[s] = None
#         # __ Dashboard Event Loop State Info _________________________________
#         listener_traffic = partial(DashboardThread.send_msg_to_listeners, sessions)
#         # __ Queue Dashboard Events __________________________________________
#         events.call_periodic(
#             delay=5, # Wait 5 seconds before first running the task
#             interval=10, # Schedule task to be run 3 seconds after it runs
#             task=listener_traffic
#         )
#         # __ Dashboard Event Loop Start ______________________________________
#         logging.info(f"[DASHBOARD]: Starting DASHBOARD event loop")
#         while getattr(self.t, 'running', True):
#             ready2read, _, _ = select.select(sessions, [], [], 0.1)
#             for c in ready2read:
#                 if c is s:  # If the Socket Server has a connection request
#                     self.connect(c, sessions)
#                     continue
#                 # If we get to this point then a client has sent a message
#                 line = c.recv(8)  # Listener <- Dashboard
#                 (length,) = unpack('>Q', line)
#                 data = self.recvall(c, length)
#                 if data: # If they sent anything (even a blank return)
#                     msg = normalspeak(data)
#                     logging.info(f"[DASHBOARD]: Received '{msg}' from LISTENER")
#                 else: # If they sent nothing (which for TCP, happens when client disconnects)
#                     logging.info(f"[DASHBOARD]: Disconnecting {sessions[c].address}")
#                     self.disconnect_client(c, sessions)
#             # Now check if any scheduled task is ready to be run
#             events.run_scheduled_tasks() # Runs any scheduled task
#
#         # __ Dashboard Event Loop Cleanup ____________________________________
#         self.disconnect_all(sessions)


# __ Listener Thread _________________________________________________________
class ListenerThread(BaseCommThread):

    def __init__(self, addr, *dash_addrs):
        '''
        Initializes the Listener's address & the addresses of the Dashboards it
        is connected to.
        Note: All address arguments must be in the following form:
            ("127.0.0.1", 16000)
        '''
        super().__init__()
        self.addr = addr  # Listener's own address
        self.dash_addrs = dash_addrs # Only used initially to start the Listener
                                     # off with a dashboard connection
        self.q = Queue()

    @staticmethod
    def dashboard_adder(sessions, q):
        '''
        Periodic task to check if any new dashboardd need to be added
        TODO: Finish the part where you actually add the dashboard that needs
              to be added lol.
        '''
        if not q.empty():
            print(f"Additional DASHBOARDS found: {q}")# <---------------------------------- MAKE A FUNCTION TO PARSE QUEUE INPUT

    @staticmethod
    def add_dash(addr, session):
        '''
        Used to add additional Dashboards to the Listener
        '''
        c = create_non_blocking_tcp_client(*addr)
        id = uuid.uuid4()
        logging.info(f"[LISTENER]: Adding LISTENER:{id} & connecting it to DASHBOARD {addr} ")
        session[c] = DashSession(addr, c, id)

    @staticmethod
    def connect(c, a, session):
        '''
        Adds any inbound sockets to the Listner
        '''
        id = uuid.uuid4()
        session[c] = PipeSession(a, c, id)

    @staticmethod
    def disconnect_client(sessions, c):
        '''
        Disconnects any socket that was originally inbound
        '''
        client = 'PIPE' if isinstance(sessions[c], PipeSession) else 'DASH'
        id = sessions[c].id
        c.close()
        logging.info(f"[LISTENER]: Disconnecting LISTENER:{id} from {client}")
        del sessions[c]

    @staticmethod
    def disconnect_all(sessions):
        '''
        Disconnects all inbound sockets and then shuts down the Listener socket
        '''
        clients = [c for c in sessions if sessions[c]]
        map(partial(DashboardThread.disconnect_client, sessions), clients)
        for s in sessions.keys():  # Kill the Socket Server last
            s.close()

    @staticmethod
    def recvall(c, length):
        '''Convenience function to read large amounts of data (>4096 bytes)'''
        data = b''
        while len(data) < length:
            remaining = length - len(data)
            data += c.recv(min(remaining, 4096))
        return data

    def run(self):
        '''
        The Listener itself.
        TODO: 1.) Sort input from Dashboard to correct buffer for specified PIPE
              2.) Same as 1.) except from PIPE to Dashboard
              3.) Change all communication from Listener to Pipe to UDP
        '''
        t = threading.current_thread()  # Grab current threading context
        # __ Dashboard Event Loop State Info _________________________________
        sessions = {}    # { csocket : PipeSession(address, file)}
        data2pipes = []  # [buffer for data from DASHBOARD to PIPES]
        data2dash = []   # [buffer for data from PIPES to DASHBOARD]
        events = EventQueue()  # Class that queues events
        # __ Initialize Dashboard Event Loop States __________________________
        s = create_non_blocking_tcp_server(*self.addr) # Create the PIPER
        sessions[s] = None  # Add PIPER to sessions, it talks to the PIPES
        [self.add_dash(addr, sessions) for addr in self.dash_addrs]
        # __ Dashboard Adder Function Initialization  ________________________
        dash_adder = partial(ListenerThread.dashboard_adder,
                             sessions=sessions,
                             q=self.q)
        # __ Queue Dashboard Events __________________________________________
        events.call_periodic(
            delay=5, # Wait 5 seconds before first running the task
            interval=3, # Schedule task to be run 3 seconds after every call
            task=dash_adder # What to call
        )
        # __ Dashboard Event Loop Start ______________________________________
        logging.info(f"[LISTENER]: Starting LISTENER event loop")
        while getattr(t, 'running', True):
            ready2read, ready2write, _ = select.select(sessions,sessions,[],0.1)
            for c in ready2read:
                if c is s: # If the PIPES are calling lol
                    c, a = c.accept()
                    self.connect(c, a, sessions)
                    # Check if there is data for the PIPE
                    msg = heappop(data2pipes) if data2pipes else '' # <---------------------------------- MAKE A FUNCTION TO RETRIEVE BY PIPEID IN JSON
                    msg_str = f" '{msg}' available from pipequeue" if msg else " No Data Available"
                    logging.info(f"[LISTENER:PIPER]: PIPE {a} "
                                 f"requested data, {msg_str}")
                    # Pack data & send
                    msg_b = sockspeak(msg)
                    length = pack('>Q', len(msg_b))
                    c.sendall(length)  # Listener -> Pipes
                    c.sendall(msg_b)  # Listener -> Pipes
                    # recvdata
                    line = c.recv(8)  # Listener <- Pipes
                    (length,) = unpack('>Q', line)
                    data = self.recvall(c, length)
                    # disconnect client and parse & store data
                    self.disconnect_client(sessions, c)
                    msg = normalspeak(data)
                    logging.info(f"[LISTENER:PIPER]: Received '{msg}' from {a}, adding to dashqueue")
                    heappush(data2dash, msg)  # <----------------------------- MAKE A FUNCTION TO SORT BY PIPEID IN JSON
                else: # If one of the many DASHBOARDs are calling
                    id = sessions[c].id
                    # Unpack data & parse
                    line = c.recv(8)  # Listener <- Dashboard
                    (length,) = unpack('>Q', line)
                    data = self.recvall(c, length)
                    if data:
                        msg = normalspeak(data)
                        logging.info(f"[LISTENER:{id}]: Received '{msg}' from its DASHBOARD")
                        heappush(data2pipes, msg) # <---------------------------------- MAKE A FUNCTION TO SORT BY PIPEID IN JSON
                    else:
                        self.disconnect_client(sessions, c)
            # Check if there is any data to be sent back to the DASHBOARDs
            if data2dash:
                for c in ready2write:
                    # Never write to PIPES without consent. We do that above
                    if c is s or isinstance(sessions[c], PipeSession): continue
                    # The logic for sending what PIPE message to which DAHBOARD
                    # is yet to be decided (based on json format) ?
                    id = sessions[c].id
                    while data2dash:
                        msg = heappop(data2dash) # <---------------------------------- MAKE A FUNCTION TO RETRIEVE BY PIPEID IN JSON
                        logging.info(f"[LISTENER:{id}]: Sending '{msg}' to its DASHBOARD")
                        # pack data and send
                        msg_b = sockspeak(msg)
                        length = pack('>Q', len(msg_b))
                        c.sendall(length)   # Listener -> Dashboard
                        c.sendall(msg_b)   # Listener -> Dashboard

            # Now check if any scheduled task is ready to be run
            events.run_scheduled_tasks() # Runs any scheduled task

        # __ Dashboard Event Loop Cleanup ____________________________________
        self.disconnect_all(sessions)


# [JEFF] DO NOT DELET, this is older code for Listener but is now relevant as we
#        are changing to UDP again for the Pipes.
# __ Old Listener_____________________________________________________________
# from heapq import heappush, heappop
# def main(host=DEFAULT_HOST, port=DEFAULT_PORT):
#     'Version with event loop'
#     data2pipes = []
#     data2dash = []
#     events = []
#
#     t = spawn_server_thread() # This is supposed to emulate the Dashboard Chat Room
#     t.start()
#     time.sleep(1)
#     sorbet = create_non_blocking_udp_server(host, port) # Listener <-> Pipes
#     croissant = create_non_blocking_tcp_client(AUXILARY_HOST, AUXILARY_PORT) # Listener <- Dashboard
#     try:
#         while RUN:
#             ready2read, ready2write, _ = select.select([sorbet, croissant], [croissant], [], 0.1)
#             # Check each socket for data that was written to it
#             for c in ready2read:  # for each socket that has data ready to read
#                 col = next(CYCLE_COLORS) # UNNECESSARY TERMINAL COLORING
#                 if c is sorbet: # If data is ready to be read from socket server
#                     line, addr = c.recvfrom(2048)  # Listener <- Pipes
#                     if line.rstrip().startswith(b'Request'):  # Pipe is requesting data
#                         print(col+f"[LISTENER:sorbet]: Received Request for info from {addr}", end='')
#                         # Grab the REQUESTING PIPE'S data IF there is data the
#                         # DASHBOARD sent specifically for the REQUESTING PIPE
#                         msg = heappop(data2pipes) if data2pipes else '' # This does not implement the logic in the the comments above
#                         print(f" '{msg}' available from pipequeue" if msg else ", No Data Available")
#                         c.sendto(sockspeak(msg), addr)  # Listener -> Pipes
#                     else: # Pipe wishes to send data to Dashboard
#                         msg = normalspeak(line)
#                         print(col+f"[LISTENER:sorbet]: Received '{msg}' from {addr}, adding to dashqueue")
#                         heappush(data2dash, msg)  # Add message to dashboard 'queue'
#                 else: # Received data from Dashboard
#                     line = c.recv(2048)  # Listener <- Dashboard
#                     msg = normalspeak(line)
#                     print(col+f"[LISTENER:croissant]: Received '{msg}' from DASHBOARD, adding to pipequeue")
#                     # PARSE THE LINE AND DUMP THE DATA INTO THE RESPECTIVE
#                     heappush(data2pipes, msg) # This does not implement the logic above
#             # Check if there is even any data to write
#             if data2dash:
#                 # Check each socket that is ready to write (all sockets are usually ready to write)
#                 for c in ready2write:
#                     col = next(CYCLE_COLORS)  # UNNECESSARY TERMINAL COLORING
#                     if c is croissant:  # Only Croissant can write to DASHBOARD so this is just a sanity check
#                         while data2dash:
#                             data = heappop(data2dash) # Grab single item from 'queue'
#                                                       # Note: you can also repetitively send
#                                                       # until 'queue' is empty. Here we send
#                                                       # one item and then check for data
#                                                       # coming from pipes & repeat.
#                             print(col+f"[LISTENER:croissant]: sending '{data}' from dashqueue to DASHBOARD")
#                             c.sendall(sockspeak(data))  # Listener -> Dashboard
#
#     except KeyboardInterrupt:
#         print("[SERVER]: Caught Keyboard Interrupt")
#     t.running=False
#     t.join()
#     sorbet.close()
#     croissant.close()



# [JEFF] All the stuff below is for simulating PIPEs sending data to the Listener
# __ UDP Client Protocols ____________________________________________________
# class TCPPipeProtocol(asyncio.Protocol):
#     def __init__(self, id, is_done):
#         self.id = id  # UDP connection's unique ID
#         self.is_done = is_done  # awaitable object (for external use)
#         self.transport = None  # The UDP connection
#
#     def connection_made(self, transport):
#         self.transport = transport
#         addr = self.transport.get_extra_info('peername')
#         logging.info(f'[PIPE:{self.id}]: Connected to \'{addr}\'')
#
#     def data_received(self, data):
#         logging.info(f'[PIPE:{self.id}]: Received \'{data.decode()}\'')
#         # Some buullllshiieettt v v v v v v
#         self.msg = "PIPE data to DASHBOARD"
#         length = pack('>Q', len(self.msg.encode()))
#         self.transport.write(length)
#         self.transport.write(self.msg.encode())
#         logging.info(f'[PIPE:{self.id}]: Sending \'{self.msg}\'')
#         self.disconnect()
#
#     def eof_received(self):
#         self.is_done.set_result(True)
#         self.disconnect()
#
#     def connection_lost(self, exc):
#         if not self.is_done.done():
#             self.is_done.set_result(True)
#
#     def disconnect(self):
#         self.transport.close()
#         logging.info(f'[PIPE:{self.id}]: DISCONNECTED')
#
#
# async def create_pipe(id, addr, loop):
#     is_done = loop.create_future()
#     transport, protocol = await loop.create_connection(
#         lambda: TCPPipeProtocol(id, is_done),
#         host=addr[0],
#         port=addr[1]
#     )
#     try:
#         await is_done
#     finally:
#         transport.close()
#
# async def create_pipes(addr, num_pipes=1):
#     loop = asyncio.get_running_loop()
#     tasks = [create_pipe(next(FISH), addr, loop) for r in range(num_pipes)]
#
#     result = await asyncio.gather(*tasks, return_exceptions=True)
#     print(f"PIPE errors = {result}")
#
# def endless_pipe(addr):
#     while True:
#         num_pipes = randint(1,3)
#         asyncio.run(create_pipes(addr, num_pipes))
#         print("Pipes are recharging...")
#         time.sleep(15)


# [JEFF] This is where I start the simulated communication (kill via Ctrl+c)
# if __name__ == '__main__':
#     from uuid import uuid4
#
#     DASH_ADDR = ("127.0.0.1",  8000)
#     LIST_ADDR = ("127.0.0.1", 16000)
#
#     try:
#         d = DashboardThread(DASH_ADDR)
#         d.start()
#         l = ListenerThread(LIST_ADDR, DASH_ADDR)
#         l.start()
#         time.sleep(5)
#         endless_pipe(LIST_ADDR)
#     finally:
#         d.stop_thread()
#         l.stop_thread()
