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

from plugins.util import *


@command()
def admincommands(bot, *args):
    """Say the list of admin commands to the channel."""
    bot.say(args[1], "My commands are: {}".format(", ".join(bot.admin_commands)))


@command()
def adminlist(bot, *args):
    """Say the list of current bot operators to the channel."""
    if len(bot.settings['botop']) > 1:
        bot.say(args[1], "My bot operators are {}.".format(', '.join(bot.settings['botop'])))
    elif len(bot.settings['botop']) == 1 and bot.settings['botop'][0] != '':
        bot.say(args[1], "My bot operator is {}.".format(bot.settings['botop'][0]))
    else:
        bot.say(args[1], "{0} has no master. {0} is a free bot.".format(bot.settings['nick']))


@command('commandlist')
def commands(bot, *args):
    """Say the list of commands to the channel."""
    bot.say(args[1], "My commands are: {}".format(", ".join(bot.commands)))
