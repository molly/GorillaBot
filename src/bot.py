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

import sys
import logging
from config import Configure
from connect import Connection
from commandmanager import CommandManager

sys.path += ['plugins'] 

class Bot(object):
    '''The Bot class is the core of the bot. It creates the connection and the responder. All messages
    that are received come through here, and are dispatched accordingly.'''
    
    def __init__(self, path, default, quiet):
        '''Constructs the bot object. Takes path, default, and quiet arguments from the command
        line input and sets the bot accordingly. Initializes logging, creates instances of
        necessary classes. Loads plugings, begins the connection.'''
        self._config_path = path
        self._default = default
        self._quiet = quiet
        self.logger = logging.getLogger("GorillaBot")
        self._configuration = Configure(self._config_path, self._default, self._quiet)
        settings = self._configuration.get_configuration()
        
        self.GorillaConnection = Connection(self, settings["host"], settings["port"],
                                            settings["nick"], settings["ident"],
                                            settings["realname"], settings["chans"])
        self.GorillaCommander = CommandManager(self, self.GorillaConnection)
        self.GorillaConnection._connect()
        
    def dispatch(self, line):
        '''Determines the type of message received:
                If the message is a ping, it pongs back.
                If the message is from NickServ, it determines identification status.
                If the message contains a reply code, it forwards it to parse_number.
                If the message is a PRIVMSG, it forwards it to parse_message.'''
        
        # Probably will want to remove this at some point in the future, but for now I'm going
        # to hold on to it for debugging.
        self.logger.debug(line)
        
        # Responds to ping messages. Doesn't bother to send it to the CommandManager.
        if "PING" in line[0]:
            self.logger.debug("Ping received.")
            self.GorillaConnection.pong(line[1][1:])
            
        # Identifies messages from NickServ, sends to CommandManager
        elif "NickServ" in line[0]:
            self.GorillaCommander.nickserv_parse(line)
            
        # Identifies server message codes, sends to CommandManager
        elif len(line[1])==3:
            self.GorillaCommander.process_numcode(line[1], line)
            
        # Identifies PRIVMSGs, sends to CommandManager
        elif line[1]=="PRIVMSG":
            self.GorillaCommander.check_command(line)

    def process_number(self, message_number, line):
        '''Parses a message with a reply code number and responds accordingly.'''
        if message_number == "396":
            # RPL_HOSTHIDDEN - Cloak set.
            self.logger.info("Cloak set as {}.".format(line[3]))
        elif message_number == "433":
            # ERR_NICKNAMEINUSE - Nickname is already in use.
            self.logger.error("Nickname is already in use. Closing connection.")
            self.GorillaConnection.shut_down()
        elif message_number == "442":
            # ERR_NOTONCHANNEL - You're not in that channel
            self.logger.info("You tried to part from {}, but you are not in that "
                             "channel.".format(line[3]))
        elif message_number == "470":
            self.logger.error("Unable to join channel {}.".format(line[3]))
            self.logger.info("Forwarded to {}. Parting from this channel.".format(line[4]))
            self.GorillaConnection.part(line[4], "Forwarded to unwanted channel.")
            