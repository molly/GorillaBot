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

def commands(c, channel, command_type, line):
    '''Display a list of commands the bot recognizes.'''
    if command_type == "private":
        # Any commands you want to hide from the list (e.g. regex-triggered commands)
        hide_commands = ["alfred"]
        # Any commands that need to be added to the list
        add_commands = ["notify"]
        commands = list(c.con._commands.keys())
        for remove_command in hide_commands:
            if remove_command in commands:
                commands.remove(remove_command)
        for add_command in add_commands:
            if add_command not in commands:
                commands.append(add_command)
        commands.sort()
        commands = ", ".join(commands)
        c.con.say("I know the following commands: {}. For further documentation, see "
                 "http://git.io/pNQS6g.".format(commands), channel)
    else:
        c.con.say("Documentation of my commands is available at "
                 "http://git.io/pNQS6g, or see a list by typing this "
                 "command in a private message.", channel)

def help(c, channel, command_type, line):
    '''Display a help message.'''
    c.con.say("Hello, I'm your friendly neighborhood {}! I perform a number of commands"
             " that you can view by typing !commands in a private message, or going to "
             "http://git.io/pNQS6g.".format(c.con._nick), channel)