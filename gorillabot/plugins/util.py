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

from urllib.request import Request, urlopen, URLError
from random import choice
import os
import pickle


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


def get_line(m, file):
    """Get a random line from the given file."""
    with open(m.bot.base_path + '/plugins/responses/' + file, 'r') as resps:
        lines = resps.read().splitlines()
        l = choice(lines)
        return l


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
            if title:
                data = html.read(5000).decode('utf-8')
            else:
                data = html.read().decode('utf-8')
        except UnicodeDecodeError as e:
            m.bot.logger.info("{0}: {1}".format(url, e.reason))
            return None
        else:
            return data


def humanize_list(l):
    """Return a human-readable list."""
    if len(l) == 1:
        return l[0]
    elif len(l) == 2:
        return "{0} and {1}".format(l[0], l[1])
    else:
        return ", ".join(l[:-1]) + ", and " + l[-1]
