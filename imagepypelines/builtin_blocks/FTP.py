# @Email: jmaggio14@gmail.com
# @Website: https://www.imagepypelines.org/
# @License: https://github.com/jmaggio14/imagepypelines/blob/master/LICENSE
# @github: https://github.com/jmaggio14/imagepypelines
#
# Copyright (c) 2018-2019 Jeff Maggio, Nathan Dileas, Ryan Hartzell
#
import ftplib
import io
from .. import SimpleBlock


class FTP(SimpleBlock):
    def __init__(self, host, user, passwd, remote_cwd=None, tls=True, timeout=30):
        io_kernel = {io.IOBase : str}

        if tls:
            self.session = ftplib.FTP_TLS(host, user, passwd, timeout=30)
            self.session.prot_p()
        else:
            self.session = ftplib.FTP(host, user, passwd, timeout=30)

        if remote_cwd is not None:
            self.session.cwd(remote_cwd)


        super().__init__(io_kernel,
                        requires_training=False,
                        requires_labels=False)



    def process(self, datum):
        try:
            self.session.storbinary("STOR " + '3Dprinter.png', datum)
        except ftplib.all_errors:
            return False

        return True

    def __del__(self):
        if hasattr(self,'session'):
            self.session.quit()
