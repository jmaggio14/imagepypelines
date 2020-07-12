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
class DashboardComm(object):
    clients = []
    """Object to send messages from the pipelines to dashboard(s)
    """

    # --------------------------------------------------------------------------
    @classmethod
    def connect(cls, host, port):
        new_client = TCPClient().connect()
        # maybe make this a dictionary at some point?
        cls.clients.append( new_client )

    # --------------------------------------------------------------------------
    def write(self, update_json):
        for cli in self.clients:
            cli.write(update_json)

    # IN THE FUTURE
    # def read()
