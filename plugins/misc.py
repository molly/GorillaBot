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

from plugins.util import admin, command

@command("admins")
def adminlist(m):
    """Provide a list of current bot admins."""
    cursor = m.bot.db_conn.cursor()
    cursor.execute('''SELECT nick FROM users WHERE botop = 1''')
    data = cursor.fetchall()
    cursor.close
    ops = [x[0] for x in data] 
    if ops:
        print(ops)
        if len(ops) == 1:
            m.bot.private_message(m.location, "My bot admin is " + ops[0] + ".")
        else:
            m.bot.private_message(m.location, "My bot admins are " + ", ".join(ops) + ".")
    else:
        nick = m.bot.get_setting("nick")
        m.bot.private_message(m.location, "{0} has no master. {0} is a free bot.".format(nick))


@admin("set")
def setcommand(m):
    """Adjust the settings on a command."""
    if len(m.line) < 3:
        m.bot.private_message(m.location, "Please format the command: !set [command] [setting]")
    else:
        command = m.line[1].lower()
        setting = m.line[2].lower()
        m.bot.command_settings[command] = setting
        m.bot.logger.info("Command \"" + command + "\" set to " + setting + " by " + m.sender + ".")
        m.bot.private_message(m.location, "Command \"" + command + "\" set to " + setting + ".")
