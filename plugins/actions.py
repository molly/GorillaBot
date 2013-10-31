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

from plugins.util import *
from random import choice
import re


@command('hugs', 'glomp', 'tackleglomp', 'tacklehug')
def hug(bot, *args):
    """Hugs a specified user, or hugs the channel in general."""
    regex = re.compile("(\w+)(?:(?:^and)?,\s(\w+))?(?:,?\s?and?\s?(\w+))?",
                       re.IGNORECASE)
    r = re.search(regex, " ".join(args[2]))
    sender = get_sender(args[0])
    if r and args[1] != bot.settings['nick']:
        for user in r.groups():
            if user:
                if user == bot.settings['nick']:
                    bot.me("hugs {} back.".format(sender), args[1])
                else:
                    with open(bot.base_path +
                                      '/plugins/responses/hugs.txt',
                              'r') as hugs:
                        lines = hugs.read().splitlines()
                        raw_line = choice(lines)
                        hug_line = raw_line.format(target=user)
                        bot.me(args[1], hug_line)
    elif args[1] == bot.settings['nick']:
        # This was sent as a private message
        sender = get_sender(args[0])
        bot.me(sender, "hugs {} back.".format(sender))
    else:
        bot.me(args[1], "distributes hugs evenly among the channel.")


@command('pickupline')
def flirt(bot, *args):
    """Flirts at a user, or at no one in particular."""
    regex = re.compile(
        "(?:\swith\s)?(\w+)(?:(?:^and)?,\s(\w+))?(?:,?\s?and?\s?(\w+))?",
        re.IGNORECASE)
    r = re.search(regex, " ".join(args[2]))
    with open(bot.base_path + '/plugins/responses/pickuplines.txt') as flirts:
        lines = flirts.read().splitlines()
    raw_line = choice(lines)
    if r and args[1] != bot.settings['nick']:
        for user in r.groups():
            if user:
                if user == bot.settings['nick']:
                    sender = get_sender(args[0])
                    flirt_line = raw_line.format(user=sender)
                    bot.say(args[1], flirt_line)
                else:
                    flirt_line = raw_line.format(user=user)
                    bot.say(args[1], flirt_line)
    else:
        sender = get_sender(args[0])
        flirt_line = raw_line.format(user=sender)
        bot.say(args[1], flirt_line)
