# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell
#
from .util import TCPClient
from ..Logger import get_master_logger
from .Exceptions import DashboardWarning

import logging
import json

URL_ENDPOINT = '/api/log'

def connect_to_dash(name, host, port):
    """Connects every pipeline in this session to
    """
    add_dash_logging_handler(host,port)
    DashboardComm.connect(name, host, port)

def n_dashboards():
    """returns the number of connected dashboards"""
    return len(DashboardComm.clients)

    # TODO: update the logging handler to send logging messages to the dashboard


def add_dash_logging_handler(host, port):
    # TODO 10/25/20: add secure communication
    handler = logging.HTTPHandler("{host}:{port}",
                                    URL_ENDPOINT,
                                    method='POST',
                                    secure=False,
                                    credentials=None,
                                    context=None)

    formatter = logging.Formatter( json.dumps(
                                {
                                 'type':'log',
                                 'payload':{
                                     'time':'%(asctime)s', # datetime as YYYY-MM-DD HH:MM:SS, msecs’
                                     'name':'%(name)s',
                                     'id': '%(pipeline_id)s', #{name}.{last 6 chars of uuid}
                                     'uuid': '%(pipeline_uuid)s', # universal unique id for pipeline
                                     'name': '%(pipeline_name)s', # 
                                     'level':'%(levelname)8s', # INFO, WARNING, ERROR, etc
                                     'message':'%(message)s', # Logging message
                                     }
                                 }
                             ))

    handler.setFormatter(formatter)

    get_master_logger().addHandler(handler)



################################################################################
# TODO: This dashboard system currently relies on the connect_to_dash() being called
# before the Pipeline has been instanitated. This needs to be corrected
# TODO: add method to disconnect from a specific dashboard
# TODO: better docstring
class DashboardComm(object):
    """Object to send messages from the pipelines to dashboard(s)
    """
    clients = {}
    """list of :obj:`TCPClient`: class level variable containing a list of all
    TCPclients that are connected"""
    graphs_msg_cache = {}
    """cache of pipeline update messages, these are messages that the dashboard
    needs to interpret the pipeline status messages"""

    # --------------------------------------------------------------------------
    @classmethod
    def connect(cls, name, host, port):
        """establishes a connection with the Dashboard Chatroom at the given
        host and port

        Args:
            name(str): human readable name of

            host(str): ip address for the dashboard

            port(int): port on host for the dashboard
        """
        raise_warning = False
        try:
            new_client = TCPClient().connect(host, port)
            cls.clients[name] = new_client

            # send the pipeline graph messages to new clients so they can interpret new
            # status and reset messages
            # (@Jai, will these work being send one after another like this????)
            for rep in cls.graphs_msg_cache.values():
                new_client.write(rep)

        except ConnectionRefusedError:
            msg = f"unable to connect to Dashboard at {host}:{port}"
            get_master_logger().error(msg)
            raise_warning = True

        # if raise_warning:
        #     raise DashboardWarning(msg)

    # --------------------------------------------------------------------------
    @classmethod
    def disconnect_all(cls):
        """disconnects from all dashboard servers"""
        for cli in cls.clients.values():
            cli.disconnect()

        cls.clients.empty()

    # --------------------------------------------------------------------------
    @classmethod
    def disconnect(cls, name):
        """disconnects from an individual dashboard server"""
        cls.clients[name].disconnect()
        cls.clients.pop(name)

    # --------------------------------------------------------------------------
    @property
    def total(self):
        """returns total number of connected dashboards"""
        return len(self.clients)

    # --------------------------------------------------------------------------
    def write(self, msg, names=None):
        """sends the given message to all connected dashboard servers

        Args:
            msg(str): a string to send

            names(tuple(str)): iterable of names specifying a whitelist
        """
        if names is None:
            names = self.clients.keys()

        for name in names:
            self.clients[name].write(msg)

    # --------------------------------------------------------------------------
    def read(self, names=None):
        """send delete messages to all dashboard servers"""
        if names is None:
            names = self.clients.keys()

        for name in names:
            try:
                msg = self.clients[name].read()
            except BlockingIOError:  # Case for no data ready
                msg = None
            return msg

    # --------------------------------------------------------------------------
    def write_graph(self, pipeline_id, graph_msg):
        """send pipeline graph or task changes to the Dashboard"""
        # # DEBUG ONLY
        # with open("graph.json",'w') as f:
        #     f.write(graph_msg)
        # # END DEBUG
        # update internal variable tracking pipeline graph messages
        self.graphs_msg_cache[pipeline_id] = graph_msg
        # send messages to all servers
        self.write(graph_msg)

    # --------------------------------------------------------------------------
    def write_status(self, status_msg):
        """send status changes to all Dashboards"""
        # # DEBUG ONLY
        # with open("status.json",'w') as f:
        #     f.write(status_msg)
        # # END DEBUG
        self.write(status_msg)

    # --------------------------------------------------------------------------
    def write_reset(self, reset_msg):
        """send reset messages to all dashboard servers"""
        # # DEBUG ONLY
        # with open("reset.json",'w') as f:
        #     f.write(reset_msg)
        # # END DEBUG
        self.write(reset_msg)

    # --------------------------------------------------------------------------
    def write_error(self, error_msg):
        """send error messages to all dashboard servers"""
        # # DEBUG ONLY
        # with open("error.json",'w') as f:
        #     f.write(error_msg)
        # # END DEBUG
        self.write(error_msg)

    # --------------------------------------------------------------------------
    def write_delete(self, delete_msg):
        """send delete messages to all dashboard servers"""
        # # DEBUG ONLY
        # with open("delete.json",'w') as f:
        #     f.write(delete_msg)
        # # END DEBUG
        self.write(delete_msg)






    # IN THE FUTURE
    # def read()
