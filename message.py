# Copyright (c) 2013-2014 Molly White
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


class Message(object):
    """Base class to represent a message received from the IRC server."""

    def __init__(self, bot, location, sender, body):
        self.bot = bot
        self.location = location
        self.sender = sender
        self.body = body
        self.trigger = None             # Command that this message triggers
        self.args = []                  # Args to pass to trigger command
        self.needs_own_thread = False   # Does this trigger need its own thread?
        self.set_trigger()

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        return


class Numeric(Message):
    """Represent a numeric reply from the server."""

    def __init__(self, *args):
        self.number = args[2]
        if len(args) >= 5:
            super(Numeric, self).__init__(args[0], args[3], args[1][1:], " ".join(args[4:]))
        else:
            super(Numeric, self).__init__(args[0], args[3], args[1][1:], None)

    def __str__(self):
        return "Numeric message {0}: {1}, from {2} in {3}".format(self.number, self.body,
                                                                  self.sender, self.location)

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        # TODO: RESPOND
        pass


class Notice(Message):
    """Represent a notice received from the server or another user."""

    def __init__(self, *args):
        super(Notice, self).__init__(args[0], args[3], args[1][1:], " ".join(args[4:]))

    def __str__(self):
        return "Notice from {0} in {1}: {2}".format(self.sender, self.location, self.body)

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        if self.sender == "NickServ!NickServ@services.":
            if "identify" in self.body:
                self.trigger = plugins.freenode.identify
                self.args.append(self.bot)
                self.needs_own_thread = True
            elif "ACC 0" in self.body:
                self.trigger = self.bot.join


class Ping(Message):
    """Represent a ping from the server."""

    def __init__(self, *args):
        super(Ping, self).__init__(args[0], None, args[2][1:], None)

    def __str__(self):
        return "Ping from {0}.".format(self.sender)

    def set_trigger(self):
        """Set the trigger function if this message warrants a response."""
        self.trigger = self.bot.pong
        self.args.append(self.sender)
