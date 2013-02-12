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
from Response import response_list
from urllib import parse

__all__ = ["Responder"]

class Responder(object):
    '''Checks for commands, responds to them appropriately.'''
    def __init__(self, connection):
        self._admins = ["GorillaWarfare"]
        self._GorillaConnection = connection
        self._GorillaResponses = response_list()
        self.logger = logging.getLogger("GorillaBot")
        self.bot_nick = self._GorillaConnection.nick
        self.admin_command_list = ["join", "part", "quit"]
        self.command_list = ["commands", "help", "hug", "link", "user", "usertalk"]
        
    def check_addressed(self):
        '''Checks for commands formatted as "GorillaBot: command" or "GorillaBot: !command"'''
        if self.message[0] == "GorillaBot:":
            return self.message[1:]
        else:
            return False
               
    def check_command(self, command_message):
        '''Remove any preceding exclamation points.'''
        if command_message[0][0] == "!":
            command = command_message[0][1:]
        else:
            command = command_message[0]
        command = command.lower()
        
        if command in ["hug", "hugs", "glomp", "glomps", "tacklehug", "tacklehugs"]:
            command = "hug"
        elif command in ["command", "commands"]:
            command = "commands"
        
        #Check if a valid command    
        if command in self.command_list:
            command_method = getattr(self, command)
            self.logger.info("Executing {}.".format(command))
            return command_method(command_message[1:])
        elif command in self.admin_command_list:
            self.logger.info("{} asked to execute {}.".format(self.sender_nick, command))
            if self.sender_nick in self._admins:
                command_method = getattr(self, command)
                self.logger.info("Executing {}.".format(command))
                return command_method(command_message[1:])
            else:
                self.say("Hey! You can't do that!")
            
    def check_exclamation(self):
        '''Checks for commands formatted as "!command"'''
        for idx, word in enumerate(self.message):
            if word[0] == "!":
                return self.message[idx:]
        return False
    
    def commands(self, message):
        '''Display a list of commands the bot recognizes.'''
        commands = ", ".join(self.command_list)
        self.say("I know the following commands: {}. For further documentation, see "
                 "http://git.io/pNQS6g".format(commands))
    
    def help(self, message):
        '''Display a help message.'''
        self.say("Hello, I'm your friendly neighborhood {}! I perform a number of commands"
                 " that you can view by typing !commands. Alternatively, you can see my "
                 "documentation at http://git.io/pNQS6g.".format(self.bot_nick))
    
    def hug(self, message):
        '''Hug the user back, or hug the user who hugged the bot.'''
        if len(message) == 0:
            self.me("distributes hugs evenly among the channel")
        elif message[0] == self.bot_nick:
            reply = self._GorillaResponses.hug(self.sender_nick, message[0], True)
            self.me(reply)
        else:
            self.me(self._GorillaResponses.hug(self.sender_nick, message[0]))
            
    def join(self, message):
        '''ADMIN: Join a channel.'''
        if len(message) == 1:
            channel = message[0]
            self._GorillaConnection._send("JOIN {}".format(channel))

    def link(self, message):
        '''Return a link to the Wikipedia article; formatted as !link [[Article]]'''
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
            
    def me(self, message):
        '''Say an action to the channel.'''
        self.say("\x01ACTION {0}\x01".format(message))
    
    def parse_message(self, line):
        '''Parses a message received and determines if it contains a command.'''
        r = re.search(":(.*?)!", line[0])
        if r:
            self.sender_nick = r.group(1)
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
                    
    def part(self, message):
        '''Part from a channel.'''
        channel = message[0]
        self._GorillaConnection.part(channel)
        
    def quit(self, message):
        if len(message) > 0:
            quit_message = ' '.join(message[0:])
            self._GorillaConnection._quit(quit_message)
        else:
            self._GorillaConnection._quit()
            
    def say(self, message):
        '''Say something to the channel or, if the command was received in a private message, in
        a private message to the user.'''
        if self.chan == self.bot_nick:
            self._GorillaConnection.private_message(self.sender_nick, message)
        else:
            self._GorillaConnection.private_message(self.chan, message)
            
    def user(self, message):
        '''Returns a link to the userpage; command formatted as !user Username'''
        username = ' '.join(message[0:])
        username = username.strip("[]{}").replace(" ", "_")
        url = parse.quote(username, safe="/#:")
        url = "http://en.wikipedia.org/wiki/User:" + url
        self.say(url)
        
    def usertalk(self, message):
        '''Returns a link to the user talk page; command formatted as !usertalk Username'''
        username = ' '.join(message[0:])
        username = username.strip("[]{}").replace(" ", "_")
        url = parse.quote(username, safe="/#:")
        url = "http://en.wikipedia.org/wiki/User_talk:" + url
        self.say(url)
