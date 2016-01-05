# Copyright (c) 2013-2016 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
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
import re
from time import time


class Message(object):
    """Base class to represent a message received from the IRC server."""

    def __init__(self, bot, location, sender, body):
        self.logger = logging.getLogger("GorillaBot")
        self.bot = bot
        self.location = location
        self.sender = sender
        self.body = body
        self.trigger = None  # Command that this message triggers
        self.args = []  # Args to pass to trigger command
        self.needs_own_thread = False  # Does this trigger need its own thread?
        self.is_pm = False

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        return


class Command(Message):
    """Represents a command from a user."""

    def __init__(self, *args):
        self.line = args[4:]
        self.admin = False
        super(Command, self).__init__(args[0], args[3], args[1][1:], " ".join(args[4:]))
        nick = self.bot.configuration["nick"]
        if self.line[0].strip("!:") == nick:
            self.line = self.line[1:]
        if self.location == nick:
            self.location = self.bot.parse_hostmask(self.sender)['nick']
            self.is_pm = True
        if self.line:
            self.command = self.line[0].strip("!:")
            self.set_trigger()

    def __str__(self):
        return "Command message from {0} in {1}: {2}".format(self.sender, self.location, self.body)

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        if self.bot.admin_commands and self.command in self.bot.admin_commands:
            self.admin = True
            self.trigger = eval(self.bot.admin_commands[self.command][0])
            self.args.append(self)
        elif self.bot.commands and self.command in self.bot.commands:
            self.trigger = eval(self.bot.commands[self.command][0])
            self.args.append(self)
        else:
            auto_link = self.is_pm or self.bot.get_setting('link', self.location) == 'auto'
            auto_spotify = self.is_pm or self.bot.get_setting('spotify', self.location) == 'auto'
            batman = self.bot.get_setting('batman', self.location) == 'on'
            if auto_link:
                m = re.findall(r'(https?://\S+)', self.body)
                if m:
                    self.needs_own_thread = True
                    self.trigger = plugins.link.link
                    self.args.append(self)
                    self.args.append(m)
                    return
            if auto_spotify:
                m = re.findall(r'spotify(?::|\.com)', self.body)
                if m:
                    self.needs_own_thread = True
                    self.trigger = plugins.spotify.spotify
                    self.args.append(self)
                    return
            if batman:
                if "alfredbot" in self.body.lower():
                    self.trigger = plugins.batman.alfred
                    self.args.append(self)
                    return
                if "batman" in self.body.lower():
                    self.trigger = plugins.batman.batman
                    self.args.append(self)
                    return


class Notice(Message):
    """Represent a notice received from the server or another user."""

    def __init__(self, *args):
        super(Notice, self).__init__(args[0], args[3], args[1][1:], " ".join(args[4:]))
        self.set_trigger()

    def __str__(self):
        return "Notice from {0} in {1}: {2}".format(self.sender, self.location, self.body)

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        if self.sender == "NickServ!NickServ@services.":
            if "ACC 1" in self.body:
                self.trigger = plugins.freenode.identify
                self.args.append(self)
                self.needs_own_thread = True
            elif "ACC" in self.body:
                self.trigger = self.bot.join


class Numeric(Message):
    """Represent a numeric reply from the server."""

    def __init__(self, *args):
        self.number = args[2]
        if len(args) >= 5:
            super(Numeric, self).__init__(args[0], args[3], args[1][1:], " ".join(args[4:]))
        elif len(args) == 4:
            super(Numeric, self).__init__(args[0], args[3], args[1][1:], None)
        else:
            super(Numeric, self).__init__(args[0], None, args[1][1:], None)
        self.set_trigger()

    def __str__(self):
        return "Numeric message {0}: {1}, from {2} in {3}".format(self.number, self.body,
                                                                  self.sender, self.location)

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        if self.number == "376":
            self.trigger = self.bot.get_admin
        elif self.number == "396":
            self.trigger = self.bot.join
        elif self.number in ["403"]:
            # Pass the message along
            self.logger.info(self.body)


class Ping(Message):
    """Represent a ping from the server."""

    def __init__(self, *args):
        if args[1] == "PING" or args[1] == "PONG":
            self.type = args[1]
            super(Ping, self).__init__(args[0], None, args[2][1:], None)
        else:
            self.type = args[2]
            super(Ping, self).__init__(args[0], None, args[1][1:], None)
        self.set_trigger()

    def __str__(self):
        return "{0} from {1}.".format(self.type, self.sender)

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        if self.type == "PING":
            self.trigger = self.bot.pong
            self.args.append(self.sender)
        else:
            # Record when the pong was received
            self.bot.last_received = time()


class Privmsg(Message):
    """Represents a PRIVMSG from a user."""

    def __init__(self, *args):
        super(Privmsg, self).__init__(args[0], args[3], args[1][1:], " ".join(args[4:]))
        if self.location == self.bot.configuration["nick"]:
            self.location = self.bot.parse_hostmask(self.sender)['nick']
            self.is_pm = True
        self.urls = None
        self.set_trigger()

    def __str__(self):
        return "Privmsg from {0} in {1}: {2}".format(self.sender, self.location, self.body)

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        auto_link = self.is_pm or self.bot.get_setting('link', self.location) == 'auto'
        auto_spotify = self.is_pm or self.bot.get_setting('spotify', self.location) == 'auto'
        batman = self.bot.get_setting('batman', self.location) == 'on'
        # TODO: This needs to be done better :S
        if auto_link:
            m = re.findall(r'(https?://\S+)', self.body)
            wikilinks = re.findall(r'\[{2}(.*?)\]{2}', self.body)
            if m or wikilinks:
                self.needs_own_thread = True
                self.trigger = plugins.link.link
                self.args.append(self)
                self.args.append(m)
                self.args.append(wikilinks)
                return
        if auto_spotify:
            m = re.findall(r'spotify(?::|\.com)', self.body)
            if m:
                self.needs_own_thread = True
                self.trigger = plugins.spotify.spotify
                self.args.append(self)
                return
        if batman:
            if "alfredbot" in self.body.lower():
                self.trigger = plugins.batman.alfred
                self.args.append(self)
                return
            if "batman" in self.body.lower():
                self.trigger = plugins.batman.batman
                self.args.append(self)
                return