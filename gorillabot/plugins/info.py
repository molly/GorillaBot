# Copyright (c) 2013-2015 Molly White
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
import message
from plugins.util import command, get_admin
from queue import Empty


@command("pingall", "highlightall")
def attention(m):
    """Ping everyone currently joined to the channel. Be careful to only turn this on if you trust
    those in the channel not to abuse it."""

    #-     !attention
    #-
    #- ```irc
    #- < GorillaWarfare> !attention
    #- < GorillaBot> GorillaWarfare wants your attention! user, user1, user2
    #- ```
    #-
    #- Ping all of the users in the channel.
    #-
    #- #### Settings
    #- `on` - Anyone can use this command. Be sure you trust everyone in the channel not to abuse
    #- it.
    #- `admin` - Only bot admins can use this command.

    logger = logging.getLogger("GorillaBot")
    attention_setting = m.bot.get_setting('attention', m.location)
    if attention_setting == 'admin':
        cursor = m.bot.db_conn.cursor()
        cursor.execute(
            '''SELECT nick, user, host FROM users WHERE botop = 1 AND config = ?''',
            (m.bot.configuration,))
        data = cursor.fetchone()
        cursor.close()
        if m.bot.parse_hostmask(m.sender)["host"] != data[2]:
            m.bot.private_message(m.location, "Please ask a bot operator to perform this action for"
                                              " you.")
            return
    elif attention_setting != 'on':
        return

    # Okay, we're authorized to do this.
    m.bot.response_lock.acquire()
    ignored_messages = []
    m.bot.send("NAMES {}".format(m.location))
    while True:
        try:
            msg = m.bot.message_q.get(True, 120)
        except Empty:
            logger.error("No response from server when trying to get nicks. Shutting down.")
            m.bot.shutdown.set()
            return
        if isinstance(msg, message.Numeric):
            if msg.number == '353':
                nicks = msg.body.split()
                nicks = nicks[2:]
                nicks[0] = nicks[0][1:]
                sender = m.bot.parse_hostmask(m.sender)["nick"]
                try:
                    nicks.remove(sender)
                    nicks.remove(m.bot.get_config("nick"))
                except ValueError:
                    pass
                m.bot.private_message(m.location, "{0}: {1} wants your attention"
                                      .format(", ".join(nicks), sender))
                break
        ignored_messages.append(msg)
    for msg in ignored_messages:
        m.bot.message_q.put(msg)
    m.bot.response_lock.release()



