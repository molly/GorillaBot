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


class Message(object):
    """Base class to represent a message received from the IRC server."""

    def __init__(self, location, sender, body):
        self.location = location
        self.sender = sender
        self.body = body


class Numeric(Message):
    """Represent a numeric reply from the server."""

    def __init__(self, *args):
        self.number = args[1]
        if len(args) >= 4:
            super(Numeric, self).__init__(args[2], args[0][1:], " ".join(args[3:]))
        else:
            super(Numeric, self).__init__(args[2], args[0][1:], None)

    def __str__(self):
        return "Numeric message {0}: {1}, from {2} in {3}".format(self.number, self.body,
                                                                  self.sender, self.location)


class Notice(Message):
    """Represent a notice received from the server or another user."""

    def __init__(self, *args):
        super(Notice, self).__init__(args[2], args[0][1:], " ".join(args[3:]))

    def __str__(self):
        return "Notice from {0} in {1}: {2}".format(self.sender, self.location, self.body)
