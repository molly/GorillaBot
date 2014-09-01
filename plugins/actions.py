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

from plugins.util import command, humanize_list
from random import choice
import re

@command("hugs", "glomp")
def hug(m):
    """Hugs the specified user or channel in general."""
    match = re.match(r':!(?:\w+) ?(\w+)?(?: and | |, )?((?!and)\w+)?(?:,? and |, | )?((?!and)\w+)?',
                     m.body)
    users = [x for x in match.groups() if x] if match else []
    if users == []:
        m.bot.action(m.location, "distributes {0} evenly among the channel".format(_get_hug(m)))
    else:
        bot_nick = m.bot.get_config('nick')
        for user in users:
            if user.lower() == bot_nick.lower():
                sender_nick = m.bot.parse_hostmask(m.sender)['nick']
                m.bot.action(m.location, "{0} {1} back".format(_get_hug(m), sender_nick))
                users.remove(user)
        if users != []:
            m.bot.action(m.location, "{0} {1}".format(_get_hug(m), humanize_list(users)))

def _get_hug(m):
    with open(m.bot.base_path + '/plugins/responses/hugs.txt', 'r') as hugs:
        lines = hugs.read().splitlines()
        verb = choice(lines)
        return verb