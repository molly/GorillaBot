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

import message
import os
import pickle
import queue


def admin(*args):
    """Designates bot administrator-only commands. Args is a list of command aliases."""

    def decorator(func):
        path = os.path.dirname(os.path.abspath(__file__)) + '/commands.pkl'
        try:
            with open(path, 'rb') as pickle_file:
                commands = pickle.load(pickle_file)
        except OSError:
            commands = dict()
        command_name = func.__module__ + '.' + func.__name__
        if args:
            for name in args:
                commands[name] = command_name
        commands[func.__name__] = command_name
        with open(path, 'wb') as pickle_file:
            pickle.dump(commands, pickle_file)
        return func

    return decorator


def command(*args):
    """Designates general bot commands. Args is a list of command aliases."""

    def decorator(func):
        path = os.path.dirname(os.path.abspath(__file__)) + '/admincommands.pkl'
        try:
            with open(path, 'rb') as pickle_file:
                commands = pickle.load(pickle_file)
        except OSError:
            commands = dict()
        command_name = func.__module__ + '.' + func.__name__
        if args:
            for name in args:
                commands[name] = command_name
        commands[func.__name__] = command_name
        with open(path, 'wb') as pickle_file:
            pickle.dump(commands, pickle_file)
        return func

    return decorator


def get_admin(m):
    if m.bot.settings["host"] == "irc.twitch.tv":
        # We have to treat this differently because Twitch doesn't support WHOIS
        for nick in m.bot.settings['botop']:
            nick = nick.lower()
            m.bot.ops.append(nick + "!" + nick + "@" + nick + ".tmi.twitch.tv")
    else:
        m.bot.response_lock.acquire()
        ignored_messages = []
        for nick in m.bot.settings['botop']:
            m.bot.send("WHOIS " + nick)
            while True:
                try:
                    msg= m.bot.message_q.get(True, 120)
                except queue.Empty:
                    m.bot.logger.error("No response while getting admins. Shutting down.")
                    m.bot.shutdown.set()
                    break
                else:
                    if type(msg) is message.Numeric:
                        if msg.number == '311':
                            line = msg.body.split()
                            m.bot.ops.append(line[2])
                            break
                        elif msg.number == '401':   # User isn't logged in
                            break
                        else:
                            print(msg)
                    ignored_messages.append(msg)
        m.bot.response_lock.release()
        for msg in ignored_messages:
            m.bot.message_q.put(msg)
