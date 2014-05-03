# Copyright (c) 2013-2014 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import plugins


class Command(object):
    """Represents a command received from a user."""

    def __init__(self, bot, line, command_type):
        self.bot = bot
        self.logger = logging.getLogger("GorillaBot")
        self.line = line
        self.command_type = command_type  # Type of command
        self.trigger = None  # Function this command triggers
        self.args = [self.bot]  # Arguments for command
        self.needs_own_thread = False  # Should this command be given its own thread?
        self.channel = None  # Channel in which command was received
        self.sender = None  # Nick who sent the command
        self.interpret()

    def __repr__(self):
        return '<Command type: {0}>'.format(self.command_type)

    def __str__(self):
        return (
            'Command\n\tType: {0}\n\tResponse: {1}({2})\n\tChannel: {3}\n\tSender: {4}\n\t{5}'
            .format(
                self.command_type, self.trigger, self.args, self.channel, self.sender, self.line))

    def dispatch(self, command=None):
        """Respond to a command from a user."""
        if not command:
            command = self.line[0]
            args = self.line[1:]
        else:
            args = ''
        if self.bot.admin_commands:
            if command in self.bot.admin_commands:
                if self.command_type == 'internal' or plugins.connection.is_admin(self.bot,
                                                                                  self.sender):
                    self.trigger = eval(self.bot.admin_commands[command])
                    self.args.append(self.sender)
                    self.args.append(self.channel)
                    self.args.append(args)
                else:
                    self.bot.say(self.channel, "Please ask a bot operator to perform this action "
                                               "for you.")
        if self.bot.commands:
            if command in self.bot.commands:
                self.trigger = eval(self.bot.commands[command])
                self.args.append(self.sender)
                self.args.append(self.channel)
                self.args.append(args)

    def interpret(self):
        """Call the correct function to determine the command."""
        if self.command_type == 'internal':
            self.dispatch(self.line)
        elif self.command_type == 'NickServ':
            self.nickserv_command()
        elif self.command_type == 'ping' or 'ping' in self.line:
            self.logger.debug("Ping received. Ponging.")
            self.trigger = plugins.connection.pong
            self.args.append(self.line[1][1:])
        elif self.command_type == 'numcode':
            if self.line[1] == '001':
                self.trigger = plugins.connection.get_admin
                self.needs_own_thread = True
        elif self.command_type == 'private_message':
            self.sender = self.line[0]
            self.channel = self.line[2]
            if len(self.line) == 4:
                self.line = [self.line[3][1:]]
            else:
                self.line = [self.line[3][1:]] + self.line[4:]
            if self.bot.settings['nick'] in self.line[0] and len(self.line) > 1:
                self.line = self.line[1:]
            if self.line[0][0] == '!':
                self.line[0] = self.line[0][1:]
            self.dispatch()
        elif self.command_type == 'direct_message':
            self.sender = self.line[0]
            self.channel = self.line[2]
            if len(self.line) == 4:
                return
            else:
                self.line = self.line[4:]
            if self.line[0][0] == '!':
                self.line[0] = self.line[0][1:]
            self.dispatch()
        elif self.command_type == 'exclamation_message':
            self.sender = self.line[0]
            self.channel = self.line[2]
            if len(self.line) == 4:
                self.line = [self.line[3][2:]]
            else:
                self.line = [self.line[3][2:]] + self.line[4:]
            self.dispatch()
        else:
            pass

    def nickserv_command(self):
        """Respond to a command from NickServ"""
        if 'ACC' in self.line and '0' in self.line:
            # Nick isn't registered; no need to identify
            if self.bot.settings['chans'] != ['None']:
                self.trigger = self.bot.join
                self.args = [self.bot.settings['chans']]
        elif 'identify' in self.line:
            # Nick is registered; prompt for identification
            self.trigger = plugins.nickserv.identify
            self.needs_own_thread = True
