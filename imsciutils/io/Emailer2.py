#
# @Email:  jmaggio14@gmail.com
#
# MIT License: https://github.com/jmaggio14/imsciutils/blob/master/LICENSE
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
from marrow.mailer import Mailer, Message
import socket

@iu.experimental()
class Emailer(object):
    def __init__(self,recipients,subject="noreply: imsciutils automated email"):
        # build the list of recipients as a single string
        self.recipients = ','.join(recipients)
        self.subject = subject

        # set from address as imsciutils@<full domain of this computer>
        self.author = r'imsciutils@{}'.format( socket.getfqdn() )

        # build the mailer using marrow mailer
        self.mailer = Mailer( dict(transport=dict(use='smtp',host='localhost') ) )
        self.mailer.start()

        self._message = None
        import pdb; pdb.set_trace()

    def body(self,text=''):
        self.message.plain = text

    def update_subject(self,text):
        self.subject = text

    def attach(self,filename):
        self.message.attach(filename)

    def send(self):
        self.mailer.send( self.message )
        self._message = None


    @property
    def message(self):
        if self._message is None:
            return Message(author=self.author,to=self.recipients)

        return self._message

    def close(self):
        self.mailer.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    with Emailer(['jmaggio14@gmail.com']) as emailer:
        emailer.body('this is a test')
        emailer.attach(r'C:\Users\jmagg\Documents\projects\imsciutils\io\Emailer2.py')
        emailer.send()


if __name__ == "__main__":
    main()
