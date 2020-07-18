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

"""
Graph message key structure
    type : <'graph','status','reset'>
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    args : <argument names in order>
    block_docs : <dictionary of block summaries (docstrings)
    nodes : <dict of node_ids & metadata>
    edges : <dict of edge_ids & metadata>
    node-link : <note-link format of graph connections>

status message key structure
    type : <'graph','status','reset'>
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
    nodes : <dict of updated node metadata>
    edges : <dict of edge metadata>

reset message key structure
    type : <'graph','status','reset'>
    name : <user-defined name>
    id   : <human-readable id>
    uuid : <hex uuid>
"""

def connect_to_dash(name, host, port):
    """Connects every pipeline in this session to
    """
    DashboardComm.connect(name, host, port)

def n_dashboards():
    return len(DashboardComm.clients)

    # TODO: update the logging handler to send logging messages to the dashboard

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
            for rep in self.graphs_msg_cache.values():
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




    # IN THE FUTURE
    # def read()
