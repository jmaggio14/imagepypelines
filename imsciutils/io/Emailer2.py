#
# @Email:  jmaggio14@gmail.com
#
# MIT License
#
# Copyright (c) 2018 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
