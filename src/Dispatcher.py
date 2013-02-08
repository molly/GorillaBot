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
from Connect import Connection

__all__ = ["Dispatcher"]

class Dispatcher(object):
    def __init__(self):
        self.logger = logging.getLogger("GorillaBot")
        
    def dispatch(self, line):
        print (line)
        if len(line) >=2:
            if len(line[1]) == 3:
                message_type = line[1]
                self.process_number(message_type, line)
            else: 
                #self.logger.info(line)
                if "NickServ" in line[0]:
                    print (line)
                    if "identified" in line:
                        self._logger.info("Successfully identified to NickServ.")
        else:
            #self.logger.info(line)
            pass
        
    def process_number(self, type, line):
        if type is '433':
            self._logger.warning("This nickname is in use.")
            recover = ""
            while recover != "y" and recover !="n":
                recover = input("Would you like to recover this nickname? [Y/N] ")
                recover = recover.lower()
                
                