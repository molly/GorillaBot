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

def commands(connection, sender, chan, command_type, line):
    '''Display a list of commands the bot recognizes.'''
    if command_type == "private":
        commands = ", ".join(connection._commands)
        connection.say("I know the following commands: {}. For further documentation, see "
                 "http://git.io/pNQS6g".format(commands), sender)
    else:
        connection.say("Documentation of my commands is available at "
                 "http://git.io/pNQS6g", chan)

def help(connection, sender, chan, command_type, line):
    '''Display a help message.'''
    print(sender)
    connection.say("Hello, I'm your friendly neighborhood {}! I perform a number of commands"
             " that you can view by typing !commands in a private message, or going to "
             "http://git.io/pNQS6g.".format(connection._nick), chan)