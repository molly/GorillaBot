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

import logging, socket, sys
from configure import Configure
from threading import Lock, Thread

class Bot(object):
    '''The Bot class is the core of the bot. It starts the IRC connection, and
    delegates tasks to other threads.'''
    
    def __init__(self, default, log_type, quiet):
        # Store command line settings
        self.default = default
        self.log_type = log_type
        self.quiet = quiet

        self.logger = logging.getLogger('GorillaBot')
        self.configuration = Configure( self.default, self.log_type, self.quiet )
        
        self.settings = self.configuration.get_configuration()
        self.start()
   
    def connect(self):
        '''Connect to the IRC server.'''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        try:
            self.socket.connect((self.settings['host'], self.settings['port']))
        except Exception:
            self.logger.error("Unable to connect to IRC server. Check your Internet "
                                  "connection.")
        else:
            self.send("NICK {0}".format(self.settings['nick']))
            self.send("USER {0} {1} * :{2}".format(self.settings['ident'],
                                                   self.settings['host'],
                                                   self.settings['realname']))
            self.private_message("NickServ", "ACC")
            self.loop()

    def start(self):
        '''Begin the threads. The main thread is the loop that receives commands from
        the IRC channels, and responds. The "simple" thread is the thread used for
        simple commands that do not require threads of their own. More complex commands
        will create new threads as needed.'''
        Thread(name='main', target=self.connect).start()
        Thread(name='simple_commands').start()