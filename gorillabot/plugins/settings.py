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

from plugins.util import admin, command, humanize_list


@admin("set")
def setcommand(m):
    """Adjust or view the settings on a command."""

    #-     !set setting value [#channel]
    #-
    #- ```irc
    #- < GorillaWarfare> !set link auto
    #- < GorillaBot> "link" set to "auto" in ##GorillaBot.
    #- ```
    #-
    #- Change settings for a command. Allowed and default settings for a command are viewable in
    #- the command's documentation. Settings can only be edited for channels the bot is joined
    #- to, or has been joined to in the past.

    if len(m.line) > 4:
        m.bot.private_message(m.location,
                              'Too many arguments. Use "!set setting value [#channel]".')
        return

    # Get channel ID of channel from which command was sent, or from the specified channel if given.
    if len(m.line) <= 3:
        chan = m.location
    elif len(m.line) == 4:
        if m.line[3][0] != "#":
            m.bot.private_message(m.location, 'Poorly-formatted command. '
                                              'Use "!set setting value [#channel]".')
            return
        chan = m.line[3]
    chan_id = m.bot.get_chan_id(chan)
    if chan_id is None:
        m.bot.private_message(m.location,
                              "Cannot access settings for {0}. Do I know about the channel?".format(
                                  chan))
        return

    # Respond to command
    cursor = m.bot.db_conn.cursor()
    if len(m.line) == 1:
        cursor.execute('''SELECT setting, value FROM settings WHERE chan_id = ?''', (chan_id,))
        data = cursor.fetchall()
        if data == []:
            m.bot.private_message(m.location, "Nothing has been set for {0}.".format(chan))
        else:
            m.bot.private_message(m.location, (" ".join(
                map(lambda setting: ('"{0}" is set to "{1}".'.format(setting[0], setting[1])),
                    data))))
    elif len(m.line) == 2:
        cursor.execute('''SELECT value FROM settings WHERE chan_id = ? AND setting = ?''',
                       (chan_id, m.line[1]))
        data = cursor.fetchone()
        if data is None:
            m.bot.private_message(m.location,
                                  '"{0}" has not been set for {1}.'.format(m.line[1], chan))
        else:
            m.bot.private_message(m.location,
                                  '"{0}" set to "{1}" in {2}.'.format(m.line[1], data[0], chan))
    else:
        setting = m.line[1].lower()
        value = m.line[2].lower()
        cursor.execute('''INSERT INTO settings VALUES (?, ?, ?)''', (setting, value, chan_id))
        m.bot.db_conn.commit()
        cursor.close
        m.bot.logger.info(
            '"{0}" set to "{1}" in {2} by {3}.'.format(setting, value, chan, m.sender))
        m.bot.private_message(m.location, '"{0}" set to "{1}" in {2}.'.format(setting, value, chan))


@admin()
def unset(m):
    """Unset a given setting."""

    #-     !unset setting [#channel]
    #-
    #- ```irc
    #- < GorillaWarfare> !unset link
    #- < GorillaBot> "link" unset for ##GorillaBot.
    #- ```
    #-
    #- Removes the setting for a channel. This will revert to the default value. Settings can only
    #- be edited for channels the bot is joined to, or has been joined to in the past.

    if len(m.line) != 2 and not (len(m.line) == 3 and m.line[2][0] == "#"):
        m.bot.private_message(m.location,
                              'Poorly-formatted command. Use "!unset setting [#channel]".')
        return
    chan = m.location if len(m.line) == 2 else m.line[2]
    chan_id = m.bot.get_chan_id(chan)
    if chan_id is None:
        m.bot.private_message(m.location,
                              "Cannot unset setting for {0}. Do I know about the channel?".format(
                                  chan))
        return
    cursor = m.bot.db_conn.cursor()
    cursor.execute('''DELETE FROM settings WHERE setting = ? AND chan_id = ?''',
                   (m.line[1], chan_id))
    m.bot.db_conn.commit()
    cursor.close()
    if cursor.rowcount == 1:
        m.bot.private_message(m.location, '"{0}" unset for {1}.'.format(m.line[1], chan))
    else:
        m.bot.logger.info("Couldn't unset {0} for {1}.".format(m.line[1], chan))
        m.bot.private_message(m.location, "Cannot unset {0} for {1}.".format(m.line[1], chan))
