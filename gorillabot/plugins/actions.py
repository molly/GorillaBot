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

from plugins.util import command, get_line, humanize_list
from random import choice
import re


@command("hugs", "glomp")
def hug(m):
    """Hugs the specified user or channel in general."""

    #-     !hug [user ...]
    #-
    #- ```irc
    #- < GorillaWarfare> !hug
    #- * GorillaBot distributes tackle-glomps evenly among the channel
    #- < GorillaWarfare> !hug user
    #- * GorillaBot tackles user
    #- ```
    #-
    #- Hugs the user or the channel.

    if m.is_pm:
        _hug_back(m)
    else:
        match = re.match(
            r':!(?:\w+) ?(\w+)?(?: and | |, )?((?!and)\w+)?(?:,? and |, | )?((?!and)\w+)?', m.body)
        users = [x for x in match.groups() if x] if match else []
        if users == []:
            m.bot.action(m.location, "distributes {0} evenly among the channel"
                         .format(get_line(m, "hugs.txt")))
        else:
            bot_nick = m.bot.configuration["nick"]
            for user in users:
                if user.lower() == bot_nick.lower():
                    _hug_back(m)
                    users.remove(user)
            if users != []:
                m.bot.action(m.location, "{0} {1}".format(get_line(m, "hugs.txt"),
                                                          humanize_list(users)))


def _hug_back(m):
    """Helper function to return a hug."""
    sender_nick = m.bot.parse_hostmask(m.sender)['nick']
    m.bot.action(m.location, "{0} {1} back".format(get_line(m, "hugs.txt"), sender_nick))


@command("pickupline", "flirts")
def flirt(m):
    """Flirts with the specified user or channel in general."""

    #-     !flirt [user ...]
    #-
    #- ```irc
    #- < GorillaWarfare> !flirt
    #- < GorillaBot> I'm a fermata... hold me.
    #- < GorillaWarfare> !flirt user
    #- < GorillaBot> user: If you were a booger I'd rearrange the alphabet so you fell from heaven!
    #- ```
    #-
    #- Flirts at the user or the channel.

    match = re.match(r':!(?:\w+) ?(\w+)?(?: and | |, )?((?!and)\w+)?(?:,? and |, | )?((?!and)\w+)?',
                     m.body)
    users = [x for x in match.groups() if x] if match else []
    if users == []:
        m.bot.private_message(m.location, get_line(m, "flirt.txt"))
    else:
        bot_nick = m.bot.configuration["nick"]
        for user in users:
            if user.lower() == bot_nick.lower():
                users.remove(user)
                users.append(m.bot.parse_hostmask(m.sender)["nick"])
        if users != []:
            m.bot.private_message(m.location, humanize_list(users) + ": " +
                                  get_line(m, "flirt.txt"))
