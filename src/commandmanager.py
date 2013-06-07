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

from inspect import getmembers, isfunction
from time import time
import logging, re, plugins, os
from plugins import *

__all__ = ["CommandManager"]

class CommandManager(object):
    
    def __init__(self, bot, connection):
        '''Determines if a message is in fact a command, stores a list of all valid commands.'''
        self._bot = bot
        self.con = connection
        self._bot_nick = connection._nick
        self.logger = logging.getLogger("GorillaBot")
        self.command_list = {}
        self.organize_commands()
        self._throttle_list = {}
        self.plugin_path = os.path.dirname(os.path.abspath(__file__)) + '/plugins'
        
    def check_command(self, line):
        '''Messages of type PRIVMSG will be passed through this function to check if they are
        commands.'''
        # Separates the line into its four parts
        line_string = " ".join(line)
        line_string = line_string.replace("\"", "")
        line_string = line_string.replace("\'", "")
        print(line_string)
        parser = re.compile("(?:\S+?:(\S+)!\S+\s)?([A-Z]+)\s(?:([^:]+)\s)?(?::(.+))?")
        r = re.search(parser, line_string)
        channel = r.group(3)
        irc_trailing = r.group(4)

        # Verify a message was sent
        if irc_trailing != None:
            # Check if the command was sent via private message to the bot
            if channel == self._bot_nick:
                private = True
            else:
                private = False
                
            command = ""
            command_type = ""
            command_regex = re.compile("(?:!(\S+))",re.IGNORECASE)
            if private:
                command_type = "private"
                # Change channel to sender's nick so that the message is sent as a reply to the 
                # private message.
                channel = r.group(1)
                # First check if there's a exclamation-type command
                command_r = re.search(command_regex, irc_trailing)
                if command_r != None:
                    # Exclamation type command was found
                    command = command_r.group(1)
                else:
                    # No exclamation-type command; assume first word of message
                    command_r = re.search("(\S+)", irc_trailing)
                    command = command_r.group(1)
            else:
                # Check if command was addressed to the bot (with or without exclamation)
                command_regex = "{}(?::|,|)\s(?:!?(\S+))".format(self._bot_nick)
                command_r = re.search(command_regex, irc_trailing)
                if command_r != None:
                    # Directly-addressed command found
                    command_type = "direct"
                    command = command_r.group(1)
                else:
                    # Check for exclamation command
                    command_r = re.search("!(\S+)", irc_trailing)
                    if command_r != None:
                        # Exclamation command found
                        if command_r.start(1) == 1:
                            # Exclamation command at beginning of message
                            command_type = "exclamation_first"
                        else:
                            # Command is elsewhere in message
                            command_type = "exclamation"
                        command = command_r.group(1)
                        
            if command != "":
                if command in self.command_list:
                    module_name = self.command_list[command]
                    exec_string = """{0}(self,"{1}","{2}","{3}")""".format(module_name, channel, command_type, line_string)
                    print(exec_string)
                    exec(exec_string)
            else:
                # There is no command in the line.
                self.check_regex(irc_trailing, channel, line_string)
                
    def check_regex(self, message, channel, line_string):
        '''Checks an IRC message to see if it matches a regex pattern.'''
        bat_regex = re.compile("batman",re.IGNORECASE)
        bat_r = re.search(bat_regex, message)
        if bat_r:
            exec_string = """batman.alfred(self, "{0}", "regex", "{1}")""".format(channel, line_string)
            exec(exec_string)
                    
    def get_message(self, line):
        '''Isolates the trailing message from a full message string.'''
        parser = re.compile("(?:\S+?:(\S+)!\S+\s)?([A-Z]+)\s(?:([^:]+)\s)?(?::(.+))?")
        r = re.search(parser, line)
        if r:
            return r.group(4)
        else:
            return None           
        
    def get_sender(self, line):
        '''Isolates the nick of the sender of the message from a full message string.'''
        parser = re.compile("(?:\S+?:(\S+)!\S+\s)?([A-Z]+)\s(?:([^:]+)\s)?(?::(.+))?")
        r = re.search(parser, line)
        if r:
            return r.group(1)
        else:
            return None
    
    def organize_commands(self):
        '''Collects commands from the various plugins, organizes them into a dict.'''
        for module in plugins.__all__:
            module_command_list = []
            exec("module_command_list += [name for name, data in getmembers({0})"
                 "if isfunction(data)]".format(module))
            for module_command in module_command_list:
                
                # Prevents private functions from being displayed or executed from IRC
                if module_command[0] != "_":
                    exec("self.command_list['{0}'] = '{1}.{0}'".format(module_command, module))
        self.con._commands = self.command_list
            
    def nickserv_parse(self, line):
        '''Parses a message from NickServ and responds accordingly.'''
        if "identify" in line:
            self.logger.info("NickServ has requested identification.")
            self.con.nickserv_identify()
        elif "identified" in line:
            self.con._password = self.con._tentative_password
            self.logger.info("You have successfully identified as {}.".format(line[2]))
        elif ":Invalid" in line:
            self.logger.info("You've entered an incorrect password. Please re-enter.")
            self.con.nickserv_identify()
    
    def process_numcode(self, numcode, line):
        '''Parses a message with a reply code number and responds accordingly.'''
        if numcode == "396":
            # RPL_HOSTHIDDEN - Cloak set.
            self.logger.info("Cloak set as {}.".format(line[3]))
        elif numcode == "403":
            # ERR_NOSUCHCHANNEL
            self.logger.warning("No such channel exists.")
        elif numcode == "433":
            # ERR_NICKNAMEINUSE - Nickname is already in use.
            # TODO: Change response to something more productive than shutting down.
            self.logger.error("Nickname is already in use. Closing connection.")
            self.con.quit()
            self.con.shut_down()
        elif numcode == "442":
            # ERR_NOTONCHANNEL - You're not in that channel
            self.logger.info("You tried to part from {}, but you are not in that "
                             "channel.".format(line[3]))
        elif numcode == "470":
            self.logger.error("Unable to join channel {}.".format(line[3]))
            self.logger.info("You were forwarded to {}. Parting from this channel.".format(line[4]))
            self.con.part(line[4])
            
    def throttle(self, command, delay=120):
        '''Keeps track of how often a command is executed, throttling it if it is executed too
        frequently. Default delay is two minutes, but this can be set for each function.'''
        now = time()
        if (command in self._throttle_list and now - self._throttle_list[command] < delay):
            # Command was executed less than [delay] ago. Throttling command.
            self.logger.info("Command was executed {} seconds ago. Throttling command until"
                             " {} seconds have passed.".format(now - self._throttle_list[command],delay))
            return True
        else:
            self._throttle_list[command] = now
            return False
