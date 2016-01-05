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
import message
from plugins.util import admin, command, humanize_list
from queue import Empty


@command("admincommandlist")
def admincommands(m):
    """Provide a list of admin-only commands."""

    #-     !admincommands
    #-
    #- ```irc
    #- < GorillaWarfare> !admincommands
    #- < GorillaBot> My available admin commands are join, part, quit, setcommand,
    #-               and unset. See http://molly.github.io/GorillaBot for documentation.
    #- ```
    #-
    #- Say the available admin-only commands. This does not display command aliases.

    commands = [key for key in m.bot.admin_commands.keys() if not m.bot.admin_commands[key][1]]
    commands.sort()
    if len(commands) == 0:
        m.bot.private_message(m.location, "I have no available admin commands. See "
                                          "http://molly.github.io/GorillaBot for documentation.")
    elif len(commands) == 1:
        m.bot.private_message(m.location, "My available admin command is {0}. See "
                                          "http://molly.github.io/GorillaBot for "
                                          "documentation.".format(commands[0]))
    else:
        m.bot.private_message(m.location, "My available admin commands are {0}. See "
                                          "http://molly.github.io/GorillaBot for "
                                          "documentation.".format(
            humanize_list(commands)))


@command("admins", "botops", "oplist")
def adminlist(m):
    """Provide a list of current bot admins."""

    #-     !adminlist
    #-
    #- ```irc
    #- < GorillaWarfare> !adminlist
    #- < GorillaBot> My bot admin is GorillaWarfare.
    #- ```
    #-
    #- Say the current bot operators.

    ops = list(m.bot.configuration["botops"].keys())
    if ops:
        if len(ops) == 1:
            m.bot.private_message(m.location, "My bot admin is " + ops[0] + ".")
        else:
            m.bot.private_message(m.location, "My bot admins are " + humanize_list(ops))
    else:
        nick = m.bot.configuration["nick"]
        m.bot.private_message(m.location, "{0} has no master. {0} is a free bot.".format(nick))


@command("pingall", "highlightall")
def attention(m):
    """Ping everyone currently joined to the channel. Be careful to only turn this on if you trust
    those in the channel not to abuse it."""

    #-     !attention
    #-
    #- ```irc
    #- < GorillaWarfare> !attention
    #- < GorillaBot> user1, user2, user3: GorillaWarfare wants your attention
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
        if not m.bot.is_admin(m.sender):
            m.bot.private_message(m.location, "Please ask a bot operator to perform this action for"
                                              " you.")
            return
    elif attention_setting != 'on':
        m.bot.private_message(m.location, "Command not enabled.")
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
                    nicks.remove(m.bot.configuration["nick"])
                except ValueError:
                    pass
                m.bot.private_message(m.location, "{0}: {1} wants your attention"
                                      .format(", ".join(nicks), sender))
                break
        ignored_messages.append(msg)
    for msg in ignored_messages:
        m.bot.message_q.put(msg)
    m.bot.response_lock.release()


@command("commandlist", "help")
def commands(m):
    """Provide a list of commands available to all users."""

    #-     !commands
    #-
    #- ```irc
    #- < GorillaWarfare> !commands
    #- < GorillaBot> My available commands are admincommands, adminlist, commands, hug,
    #-               link, spotify, and xkcd. See http://molly.github.io/GorillaBot
    #-               for documentation.
    #- ```
    #-
    #- Say the available all-user commands. This does not display command aliases.

    commands = [key for key in m.bot.commands.keys() if not m.bot.commands[key][1]]
    commands.sort()
    if len(commands) == 0:
        m.bot.private_message(m.location, "I have no available commands. See "
                                          "http://molly.github.io/GorillaBot for documentation.")
    elif len(commands) == 1:
        m.bot.private_message(m.location, "My available command is {0}. See "
                                          "http://molly.github.io/GorillaBot for "
                                          "documentation.".format(commands[0]))
    else:
        m.bot.private_message(m.location, "My available commands are {0}. See "
                                          "http://molly.github.io/GorillaBot for "
                                          "documentation.".format(
            humanize_list(commands)))