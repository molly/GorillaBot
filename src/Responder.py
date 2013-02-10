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
import re

__all__ = ["Responder"]

class Responder(object):
    def __init__(self, connection):
        self._GorillaConnection = connection
        self.logger = logging.getLogger("GorillaBot")
        self.bot_nick = self._GorillaConnection.nick
        self.command_list = ["link"]
        
    def check_addressed(self):
        #checks for commands formatted as "GorillaBot: command" or "GorillaBot: !command"
        if self.message[0] == "GorillaBot:":
            return self.message[1:]
        else:
            return False
               
    def check_command(self, command_message):
        if command_message[0][0] == "!":
            command = command_message[0][1:]
        else:
            command = command_message[0]
        command = command.lower()
        if command in self.command_list:
            command = "self." + command + "({})".format(command_message[1:])
            self.logger.info("Executing {}.".format(command))
            exec(command)
        else:
            print("{} is not a command!".format(command))
            
    def check_exclamation(self):
        # Checks for commands formatted as "!command"
        for idx, word in enumerate(self.message):
            if word[0] == "!":
                return self.message[idx:]
        return False
    
    def link(self, message):
        if "[[" not in message[0]:
            self.say("You formatted your link incorrectly! Please format the command as !link [[article]].")
            return 0
        end_index = ""
        for idx, word in enumerate(self.message):
            if "]]" in word:
                end_index = idx
        if type(end_index) != int:
            self.say("You formatted your link incorrectly! Please format the command as !link [[article]].")
            return 0
        else:
            self.say("Linking {}.").format(message[:end_index])
    
    def parse_message(self, line):
        self.sender_nick = re.search(":(.*?)!~", line[0])
        self.chan = line[2]
        if self.chan == self.bot_nick:
            private = True
        else:
            private = False
            
        # Format message nicely
        self.message = list()
        self.message.append(line[3][1:])
        if len(line) > 4:
            for i in range(4,len(line)):
                self.message.append(line[i])
                
        # Check if message contains a command for the bot
        if private:
            command = self.message[0:]
            self.logger.debug("Received private message: {}".format(command))
            self.check_command(command)
        else:
            command = self.check_addressed()
            if command:
                self.logger.debug("Received message addressed to the bot: {}".format(command))
                self.check_command(command)
            else:
                command = self.check_exclamation()
                if command:
                    self.logger.debug("Received message beginning with an exclamation mark: {}".format(command))
                    self.check_command(command)
                    
    def say(self, message):
        if self.chan == self.bot_nick:
            self._GorillaConnection.private_message(self.sender_nick, message)
        else:
            self._GorillaConnection.private_message(self.chan, message)