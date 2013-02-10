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
from urllib import parse

__all__ = ["Responder"]

class Responder(object):
    def __init__(self, connection):
        self._GorillaConnection = connection
        self.logger = logging.getLogger("GorillaBot")
        self.bot_nick = self._GorillaConnection.nick
        self.command_list = ["link", "user", "usertalk"]
        
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
        if "[[" not in message[0] and "{{" not in message[0]:
            self.say("Please format the command as !link [[article]] or !link {{template}}.")
            return 0
        end_index = ""
        for idx, word in enumerate(self.message):
            if "]]" in word or "}}" in word:
                end_index = idx
        if type(end_index) != int:
            self.say("Please format the command as !link [[article]] or !link {{template}}.")
            return 0
        else:
            article_name = ' '.join(message[0:end_index])
            article_name = article_name.strip("[]{}").replace(" ", "_")
            url = parse.quote(article_name, safe="/#:")
            if "{{" in message[0]:
                url = "http://en.wikipedia.org/wiki/Template:" + url
            else:
                url = "http://en.wikipedia.org/wiki/" + url
            self.say(url)
    
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
            
    def user(self, message):
        username = ' '.join(message[0:])
        username = username.strip("[]{}").replace(" ", "_")
        url = parse.quote(username, safe="/#:")
        url = "http://en.wikipedia.org/wiki/User:" + url
        self.say(url)
        
    def usertalk(self, message):
        username = ' '.join(message[0:])
        username = username.strip("[]{}").replace(" ", "_")
        url = parse.quote(username, safe="/#:")
        url = "http://en.wikipedia.org/wiki/User_talk:" + url
        self.say(url)