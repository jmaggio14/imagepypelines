# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018 - 2020 Jeff Maggio, Jai Mehra, Ryan Hartzell
#
"""
# this is an example use case:

ip.connect_to_dash(host, port)
# --> would modify a class variable in the DashboardComm

ip.Pipeline(tasks={})
# --> creates instance of DashboardComm
# self.dashcomm.update(update_params)
    --> for host,port in self.dashes:
        send_update(update_params)
"""
from .util import TCPClient



def connect_to_dash(host, port):
    """Connects every pipeline in this session to
    """
    DashboardComm.connect(host, port)

    # TODO: update the logging handler to send logging messages to the dashboard

################################################################################
# TODO: This dashboard system currently relies on the connect_to_dash() being called
# before the Pipeline has been instanitated. This needs to be corrected
# TODO: add method to disconnect from a specific dashboard
# TODO: better docstring
class DashboardComm(object):
    """Object to send messages from the pipelines to dashboard(s)
    """
    clients = []
    """list of :obj:`TCPClient`: class level variable containing a list of all
    TCPclients that are connected"""
    graphs_msg_cache = {}
    """cache of pipeline update messages, these are messages that the dashboard
    needs to interpret the pipeline status messages"""

    # --------------------------------------------------------------------------
    @classmethod
    def connect(cls, host, port):
        """establishes a connection with the Dashboard Chatroom at the given
        host and port

        Args:
            host(str): ip address for the dashboard
        """
        new_client = TCPClient().connect(host, port)
        cls.clients.append( new_client )

        # send the pipeline graph messages to new clients so they can interpret new
        # status and reset messages
        # (@Jai, will these work being send one after another like this????)
        for rep in self.graphs_msg_cache.values():
            new_client.write(rep)

    # --------------------------------------------------------------------------
    @classmethod
    def disconnect_all(cls):
        """disconnects from all dashboard servers"""
        cls.clients = []

    # --------------------------------------------------------------------------
    def write(self, msg):
        """sends the given message to all connected dashboard servers"""
        for cli in self.clients:
            cli.write(msg)

    # --------------------------------------------------------------------------
    def write_graph(self, pipeline_id, graph_msg):
        """send pipeline graph or task changes to the Dashboard"""
        # update internal variable tracking pipeline graph messages
        self.graphs_msg_cache[pipeline_id] = graph_msg
        # send messages to all servers
        self.write(graph_msg)

    # --------------------------------------------------------------------------
    def write_status(self, status_msg):
        """send status changes to all Dashboards"""
        self.write(status_msg)

    # --------------------------------------------------------------------------
    def write_reset(self, reset_msg):
        """send reset messages to all dashboard servers"""
        self.write(reset_msg)


    # IN THE FUTURE
    # def read()
