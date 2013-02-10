# Copyright (c) 2013 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
from Config import Configure
from Connect import Connection

class Bot(object):
    def __init__(self, path, default, quiet):
        self._config_path = path
        self._default = default
        self._quiet = quiet
        self.logger = logging.getLogger("GorillaBot")
        self._configuration = Configure(self._config_path, self._default, self._quiet)
        settings = self._configuration.get_configuration()
        
        self.GorillaConnection = Connection(self, settings["host"], settings["port"], settings["nick"],
                   settings["ident"], settings["realname"], settings["chans"])
        self.GorillaConnection._connect()
        
    def dispatch(self, line):
        print (line)
        if "NickServ" in line[0]:
            if "identify" in line:
                self.logger.info("NickServ has requested identification.")
                self.GorillaConnection.nickserv_identify()
            elif "identified" in line:
                self.logger.info("You have successfully identified as {}.".format(line[2]))
            elif ":Invalid" in line:
                self.logger.info("You've entered an incorrect password. Please re-enter.")
                self.GorillaConnection.nickserv_identify()
        elif len(line[1])==3:
            self.process_number(line[1], line)

    def process_number(self, message_number, line):
        if message_number == "396":
            # RPL_HOSTHIDDEN - Cloak set.
            self.logger.info("Cloak set as {}.".format(line[3]))
        if message_number == "433":
            # ERR_NICKNAMEINUSE - Nickname is already in use.
            self.logger.error("Nickname is already in use. Closing connection.")
            self.GorillaConnection._quit()
            self.GorillaConnection._close()