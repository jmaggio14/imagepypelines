import imsciutils as iu
import smtplib
from email.message import EmailMessage
import mimetypes
from collections import Iterable


class Emailer(object):
    """
    Object to automatically email recipients to result of a test
    """

    def __init__(self,recipients,subject="noreply: imsciutils automated email"):
        self.server = 'localhost'
        self.subject = subject
        if isinstance(recipients,str):
            recipients = [recipients]

        self.recipients = recipients
        self.current_msg = None
        #TODO verfify that recipients are valid here

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
        return self.current_msg

    def attach(self,filename):
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
        ## TODO: error check text
        if not isinstance(text,str):
            ie.error("unable to set body because text must be a str,\
                    currently".format( type(text) ))
            return

        msg = self.get_msg()
        msg.set_content(text)


    def send(self):
        msg = self.get_msg()
        with smtplib.SMTP(self.server) as server:
            server.send_message(msg)

        self.current_msg = None
