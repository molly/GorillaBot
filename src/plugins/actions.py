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

from random import choice
import re
import os

def hug(connection, sender, chan, command_type, line):
    line.pop(0)
    if len(line) == 0:
        connection.me("distributes hugs evenly among the channel.",
                      chan)
    elif line[0] == connection._nick:
        test = "hugs {0} back.".format(sender)
        connection.me(test, chan)
    else:
        hugs = open('plugins/responses/hugs.txt')
        lines = hugs.read().splitlines()
        raw_line = choice(lines)
        hug_line = re.sub('\{target\}', '{0}', raw_line)
        connection.me(hug_line.format(line[0]), chan)
        
def flirt(connection, sender, chan, command_type, line):
    line.pop(0)
    pickups = open('plugins/responses/pickuplines.txt')
    lines = pickups.read().splitlines()
    raw_line = choice(lines)
    if len(line) == 0:
        flirt_line = re.sub('\{user\}:\s', '', raw_line)
        connection.say(flirt_line, chan)
    else:
        flirt_line = re.sub('\{user\}', '{0}', raw_line)
        connection.me(flirt_line.format(line[0]), chan)