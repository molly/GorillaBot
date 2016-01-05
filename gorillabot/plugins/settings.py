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

    # Check that this channel is in our config
    if len(m.line) <= 3:
        chan = m.location
    elif len(m.line) == 4:
        if m.line[3][0] != "#":
            m.bot.private_message(m.location, 'Poorly-formatted command. '
                                              'Use "!set setting value [#channel]".')
            return
        chan = m.line[3]
    if not chan in m.bot.configuration["chans"]:
        m.bot.private_message(m.location,
                              "Cannot access settings for {0}. Do I know about the channel?".format(
                                  chan))
        return

    # Respond to command
    settings = m.bot.configuration["chans"][chan]["settings"]
    if len(m.line) == 1:
        # Query all settings for channel
        if not settings:
            m.bot.private_message(m.location, "Nothing has been set for {0}.".format(chan))
        else:
            m.bot.private_message(m.location, (" ".join(
                map(lambda s: ('"{0}" is set to "{1}".'.format(s[0], s[1])),
                    iter(settings.items())))))
    elif len(m.line) == 2:
        # Query value of a setting in a channel
        if not settings or m.line[1] not in settings:
            m.bot.private_message(m.location,
                                  '"{0}" has not been set for {1}.'.format(m.line[1], chan))
        else:
            m.bot.private_message(m.location,
                                  '"{0}" set to "{1}" in {2}.'.format(m.line[1],
                                                                      settings[m.line[1]], chan))
    else:
        setting = m.line[1].lower()
        value = m.line[2].lower()
        m.bot.configuration["chans"][chan]["settings"][setting] = value
        m.bot.update_configuration(m.bot.configuration)
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
    if chan not in m.bot.configuration["chans"]:
        m.bot.private_message(m.location,
                              "Cannot unset setting for {0}. Do I know about the channel?".format(
                                  chan))
        return
    try:
        del m.bot.configuration["chans"][chan]["settings"][m.line[1]]
        m.bot.update_configuration(m.bot.configuration)
    except KeyError:
        # Doesn't matter if the value wasn't set to begin with
        pass
    m.bot.private_message(m.location, '"{0}" unset for {1}.'.format(m.line[1], chan))
