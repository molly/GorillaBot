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

from plugins.util import admin


@admin()
def join(m):
    """Join a channel."""

    #-     !join #channel
    #-
    #- Joins the specified channel. Only joins one channel at a time.

    if len(m.line) == 1:
        m.bot.private_message(m.location, "Please specify a channel to join.")
    else:
        chan = m.line[1]
        if chan[0] != "#":
            chan = "#" + chan
        m.bot.join(chan)
        m.bot.logger.info("Joining " + chan)


@admin("leave")
def part(m):
    """Part from the specified channel."""

    #-     !part [#channel] [message]
    #-
    #- Parts from the specified channel, or the current channel if unspecified. Only parts from
    #- one channel at a time. If a message is included, this will be used as the part message.

    part_msg = ""
    if len(m.line) == 1:
        m.bot.send("PART " + m.location + " " + part_msg)
        m.bot.logger.info("Parting from #" + m.location)
        cursor = m.bot.db_conn.cursor()
        cursor.execute('''DELETE FROM channels WHERE name = ? AND config = ?''',
                       (m.location, m.bot.configuration))
        m.bot.db_conn.commit()
        cursor.close()
        return
    channel = ""
    if len(m.line) > 2:
        part_msg = " ".join(m.line[2:])
    if m.line[1][0] != "#":
        channel = "#" + m.line[1]
    else:
        channel = m.line[1]
    m.bot.send("PART " + channel + " :" + part_msg)
    m.bot.logger.info("Parting from " + channel + ".")
    cursor = m.bot.db_conn.cursor()
    cursor.execute('''DELETE FROM channels WHERE name = ? AND config = ?''',
                   (channel, m.bot.configuration))
    m.bot.db_conn.commit()
    cursor.close()


@admin("shutdown")
def quit(m):
    """Shut down the bot entirely."""

    #-     !quit [message]
    #-
    #- Quits the bot from the network and shuts down.

    msg = " ".join(m.line[1:]) if len(m.line) > 1 else ""
    m.bot.send("QUIT :" + msg)
    m.bot.shutdown.set()