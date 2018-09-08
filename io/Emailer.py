import imsciutils as iu
import smtplib
from email.message import EmailMessage
import mimetypes
from collections import Iterable
from socket import getfqdn

from aiosmtpd.controller import Controller
import asyncio
# Class is non-functional or at least unreliable as of Sept 7th,2018
# Believe the problem is in starting / accessing a local SMTP server?
# mail sends, but never arrives
# This file will also break imports in python 2
# @Nate, I'm totally unfamiliar with SMTP stuff and am not particularly happy
# with the current implementation. Mind taking a look?
#                                   -Jeff


## TODO: automatically retrieve a free port instead of hardcoding it
ACTIVE_CONTROLLER = None
class ExampleHandler:
    """taken from https://aiosmtpd.readthedocs.io/en/latest/aiosmtpd/docs/controller.html"""
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        print(envelope.content.decode('utf8', errors='replace'))
        print('End of message')
        return '250 Message accepted for delivery'


def setup_smpt_server():
    controller = Controller( ExampleHandler() )
    controller.start()
    return controller,controller.hostname, controller.port


class Emailer(object):
    """
    WIP!

    Goal is to build an object which can be used to automatically send emails
    after a test or run completes.
    simplicity trumps functionality here, we mostly want it to be easy to use

    # NOTE:
    Class is non-functional or at least unreliable as of Sept 7th,2018
    Believe the problem is in starting / accessing a local SMTP server?
    mail sends, but never arrives
    This file will also break imports in python 2
    @Nate, I'm totally unfamiliar with SMTP stuff and am not particularly happy
    with the current implementation. Mind taking a look?
                                     -Jeff

    I've seen tons of examples using a gmail account, but we want something
    that sends from the local machine....
    as far as I'm concerned, we can just use subprocess calls to a terminal

    Example:
        emailer = iu.io.Emailer(['recipient1@example.com'],subject='example')

        # edit the body
        emailer.body("this is a sample body")

        # attach a file
        emailer.attach('filename.txt')

        # send
        emailer.send()


    """
    def __init__(self,recipients,subject="noreply: imsciutils automated email"):
        self.subject = subject

        # TODO verfify that recipients are valid here
        if isinstance(recipients,str):
            recipients = [recipients]

        self.recipients = recipients
        self.current_msg = None

        self.controller, self.server_ip, self.server_port = setup_smpt_server()

        # launch the smtp server

    def get_msg(self):
        """
        returns the current email message or creates a new one if one
        is not already queued
        """
        if self.current_msg is not None:
            return self.current_msg

        self.current_msg = EmailMessage()
        self.current_msg['Subject'] = self.subject
        self.current_msg['To'] = ', '.join(self.recipients)
        # getfqdn retrieves the full domain name for this machine
        self.current_msg['From'] = "imsciutils@{}".format( getfqdn() )
        return self.current_msg

    def attach(self,filename):
        """
        attaches a file to the email message
        """
        msg = self.get_msg()

        if not os.path.isfile(filename):
            iu.error("file '{}' does not exist or is inaccessible,\
                            skipping attachment!".format(filename))
            return
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(filename)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'

        maintype, subtype = ctype.split('/', 1)
        with open(filename, 'rb') as fp:
            msg.add_attachment(fp.read(),
                               maintype=maintype,
                               subtype=subtype,
                               filename=filename)

    def body(self,text):
        """
        sets the body of the current email message
        """
        if not isinstance(text,str):
            ie.error("unable to set body because text must be a str,\
                    currently".format( type(text) ))
            return

        msg = self.get_msg()
        msg.set_content(text)


    def send(self):
        """
        sends the current message and clears the template so a new
        message can be created
        """
        msg = self.get_msg()
        with smtplib.SMTP(self.server_ip,self.server_port) as server:
            server.send_message(msg)

        self.current_msg = None

    def close(self):
        self.controller.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


def main():
    import imsciutils as iu
    with iu.io.Emailer('jmaggio14@gmail.com') as emailer:
        emailer.body('test')
        emailer.send()


if __name__ == "__main__":
    main()
