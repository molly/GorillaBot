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

from urllib.request import Request, urlopen, URLError
import message
import os
import pickle
import re
import queue


def admin(*args):
    """Designates bot administrator-only commands. Args is a list of command aliases."""

    def decorator(func):
        path = os.path.dirname(os.path.abspath(__file__)) + '/commands.pkl'
        try:
            with open(path, 'rb') as pickle_file:
                commands = pickle.load(pickle_file)
        except (OSError, IOError):
            commands = dict()
        command_name = func.__module__ + '.' + func.__name__
        if args:
            for name in args:
                commands[name] = (command_name, True)
        commands[func.__name__] = (command_name, False)
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
        except (OSError, IOError):
            commands = dict()
        command_name = func.__module__ + '.' + func.__name__
        if args:
            for name in args:
                commands[name] = (command_name, True)
        commands[func.__name__] = (command_name, False)
        with open(path, 'wb') as pickle_file:
            pickle.dump(commands, pickle_file)
        return func

    return decorator


def get_admin(m):
    """Get the hostnames for the bot admins."""
    cursor = m.bot.db_conn.cursor()
    cursor.execute('''SELECT user_id, nick, config FROM users WHERE botop = 1''')
    botops = cursor.fetchall()
    cursor.close()
    m.bot.response_lock.acquire()
    ignored_messages = []
    for op in botops:
        if op[2] == m.bot.configuration:
            m.bot.send("WHOIS " + op[1])
            while True:
                try:
                    msg = m.bot.message_q.get(True, 120)
                except queue.Empty:
                    m.bot.logger.error("No response while getting admins. Shutting down.")
                    m.bot.shutdown.set()
                    break
                else:
                    if type(msg) is message.Numeric:
                        print(msg)
                        if msg.number == '311':
                            # User info
                            line = msg.body.split()
                            cursor = m.bot.db_conn.cursor()
                            cursor.execute('''UPDATE users SET user=?, host=? WHERE user_id=?''',
                                           (line[1], line[2], op[0]))
                            m.bot.logger.info("Adding {0} {1} to bot ops under {2}"
                                              .format(line[1], line[2], op[0]))
                            m.bot.db_conn.commit()
                            cursor.close()
                        elif msg.number == '318':
                            # End of WHOIS
                            break
                        elif msg.number == '319':
                            # Channel info
                            line = msg.body.split()
                            channels = line[1:]
                            for chan in channels:
                                chan = re.sub(r'[^#]*(?=#)', '', chan)
                                cursor = m.bot.db_conn.cursor()
                                cursor.execute(
                                    '''SELECT chan_id FROM channels WHERE name=? AND config=?''',
                                    (chan, op[2]))
                                data = cursor.fetchone()
                                cursor.execute('''INSERT INTO users_to_channels VALUES (?, ?)''',
                                               (op[0], data[0]))
                                m.bot.db_conn.commit()
                                cursor.close()
                        elif msg.number == '401':
                            # No such user
                            m.bot.logger.info("No user {0} logged in.".format(op[0]))
                            break
                    ignored_messages.append(msg)
    m.bot.response_lock.release()
    for msg in ignored_messages:
        m.bot.message_q.put(msg)

def get_url(m, url, title=False):
    """Request a given URL, handling any errors. If 'title' is True, this will only return the
    first 1000 bytes of the page in an effort to not load too much more than is necessary."""
    request = Request(url, headers=m.bot.header)
    try:
        html = urlopen(request)
    except URLError as e:
        m.bot.logger.info("{0}: {1}".format(url, e.reason))
        return None
    else:
        try:
            bytes = html.read(5000 if title else -1).decode('utf-8')
        except UnicodeDecodeError as e:
            m.bot.logger.info("{0}: {1}".format(url, e.reason))
            return None
        else:
            return bytes

def humanize_list(l):
    if len(l) == 1:
        return l[0]
    elif len(l) == 2:
        return "{0} and {1}".format(l[0], l[1])
    else:
        return ", ".join(l[:-1]) + ", and " + l[-1]
