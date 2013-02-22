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
# OUT OF OR IN c.con WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from random import choice
import re

def hug(c, channel, command_type, line):
    '''Hugs a specified user, or hugs the channel in general.'''
    regex = re.compile("!?hug\s(\w+)(?:(?:^and)?,\s(\w+))?(?:,?\s?and?\s?(\w+))?",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        for user in r.groups():
            if user:
                if user == c._bot_nick:
                    sender = c.get_sender(line)
                    c.con.me("hugs {} back.".format(sender), channel)
                else:
                    hugs = open('plugins/responses/hugs.txt')
                    lines = hugs.read().splitlines()
                    raw_line = choice(lines)
                    hug_line = re.sub('\{target\}', user, raw_line)
                    c.con.me(hug_line, channel)
    elif command_type == "private":
        sender = c.get_sender(line)
        c.con.me("hugs {} back.".format(sender), channel)
    else:
        c.con.me("distributes hugs evenly among the channel.", channel)
    
def flirt(c, channel, command_type, line):
    '''Flirts at a user, or at no one in particular.'''
    regex = re.compile("!?flirt(?:\swith)?\s(\w+)(?:(?:^and)?,\s(\w+))?(?:,?\s?and?\s?(\w+))?",re.IGNORECASE)
    r = re.search(regex, line)
    flirts = open('plugins/responses/pickuplines.txt')
    lines = flirts.read().splitlines()
    raw_line = choice(lines)
    if r and command_type != "private":
        for user in r.groups():
            if user:
                if user == c._bot_nick:
                    sender = c.get_sender(line)
                    flirt_line = re.sub('\{user\}', sender, raw_line)
                    c.con.say(flirt_line, channel)
                else:
                    flirt_line = re.sub('\{user\}', user, raw_line)
                    c.con.say(flirt_line, channel)
    else:
        r = re.search("\{user\}:\s(.*)", raw_line)
        flirt_line = r.group(1)
        c.con.say(flirt_line, channel)