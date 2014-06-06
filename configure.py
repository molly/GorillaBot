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

import configparser
from getpass import getpass
import logging
import os


class Configurator(object):
    """Deals with the configuration file. It will create a new one if one doesn't exist,
    or find or modify an existing one. """

    def __init__(self, default, file):
        self.config = configparser.ConfigParser()
        if file:
            self.config_path = os.path.dirname(os.path.abspath(__file__)) + '/' + file
        else:
            self.config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
        self.logger = logging.getLogger("GorillaBot")
        self.default = default
        self.options = ('host', 'port', 'nick', 'ident', 'realname', 'chans', 'botop', 'password',
                        'wait')

    def get_configuration(self):
        """Return configuration as a dictionary."""
        # Load existing configuration, or create a new config file.
        self.load()

        # Read config values
        host = self.config.get("irc", "Host")
        port = int(self.config.get("irc", "Port"))
        nick = self.config.get("irc", "Nick")
        realname = self.config.get("irc", "Realname")
        ident = self.config.get("irc", "Ident")
        chans = self.config.get("irc", "Chans")
        botop = self.config.get("irc", "Botop")
        password = self.config.get("irc", "Password")
        wait = self.config.get("irc", "Wait")

        # Allow comma- or space-separated lists
        if ',' in chans:
            chanlist = chans.split(',')
        else:
            chanlist = chans.split(' ')
        for i in range(len(chanlist)):
            chanlist[i] = chanlist[i].strip()
            # Ensure each channel name begins with at least one hash
            if chanlist[i][0] != '#':
                chanlist[i] = '#' + chanlist[i]

        if ',' in botop:
            oplist = botop.split(',')
        else:
            oplist = botop.split(' ')
        for i in range(len(oplist)):
            oplist[i] = oplist[i].strip()
        return {"host": host, "port": port, "nick": nick, "realname": realname, "ident": ident,
                "chans": chanlist, "botop": oplist, "password": password, "wait": wait}

    def load(self):
        """Try to load an existing configuration file. If it exists, validate it. If it does not,
        begin to create a new one. """
        try:
            self.config.read_file(open(self.config_path))
        except IOError:
            # File doesn't exist; create new one.
            self.logger.info(
                'Unable to open {}. Creating a new configuration file.'.format(self.config_path))
            self.make_new()
        else:
            # File exists; make sure it's properly formatted
            self.verify()

    def make_new(self):
        """Create a new configuration file from scratch."""
        verify = ''
        while verify != 'y':
            print('\n')
            host = self.prompt("Host", "chat.freenode.net")
            port = self.prompt("Port", 6667)
            nick = self.prompt("Nick", "GorillaBot")
            realname = self.prompt("Ident", "GorillaBot")
            ident = self.prompt("Realname", "GorillaBot")
            chans = self.prompt("Chans")
            botop = self.prompt("Bot operator(s)", '')
            password = self.prompt("Server password", hidden=True)
            wait = self.prompt("Wait to join before entering channels? [Y/N]", 'n')
            print(
                "------------------------------\n Host: {0}\n Port: {1}\n Nickname: {2}\n Real "
                "name: {3}\n Identifier: {4}\n Channels: {5}\n Bot operator(s): {"
                "6}\n Server password: {7}\n Wait to join?: {8}\n------------------------------"
                .format( host, port, nick, realname, ident, chans, botop,
                         "[hidden]" if password else "[none]", wait))
            verify = input('Is this configuration correct? [Y/N]: ').lower()
            if verify == 'y':
                break
        self.config.add_section("irc")
        self.config.set("irc", "host", host)
        self.config.set("irc", "port", str(port))
        self.config.set("irc", "nick", nick)
        self.config.set("irc", "realname", realname)
        self.config.set("irc", "ident", ident)
        self.config.set("irc", "chans", chans)
        self.config.set("irc", "botop", botop)
        self.config.set("irc", "password", password)
        self.config.set("irc", "wait", wait)
        with open(self.config_path, 'w') as config_file:
            self.config.write(config_file)
        self.logger.info("Configuration file saved.")

    def print_settings(self):
        """Display existing settings in a configuration file."""
        host = self.config.get("irc", "host")
        port = self.config.get("irc", "port")
        nick = self.config.get("irc", "nick")
        realname = self.config.get("irc", "realname")
        ident = self.config.get("irc", "ident")
        chans = self.config.get("irc", "chans")
        botop = self.config.get("irc", "botop")
        password = self.config.get("irc", "password")
        wait = self.config.get("irc", "wait")
        print("------------------------------\n Host: {0}\n Port: {1}\n Nickname: {2}\n Real "
              "name: {3}\n Identifier: {4}\n Channels: {5}\n Bot operator(s): {"
              "6}\nServer password: {7}\nWait to join?: {8}\n------------------------------".
              format(host, port, nick, realname, ident, chans, botop,
                     "[hidden]" if password else "[none]", wait))

    def prompt(self, field, default=None, hidden=False):
        """Prompt a user for input, displaying a default value if one exists."""
        if default:
            field += " [DEFAULT: {}]".format(default)
        field += ": "
        if not hidden:
            answer = input(field)
        else:
            answer = getpass(field)
        if default is not None and answer == '':
            return default
        return answer

    def reconfigure(self):
        """Overwrite the existing configuration file with a new one."""
        try:
            os.remove(self.config_path)
        except OSError:
            self.logger.error('Unable to remove existing configuration file.')
        else:
            self.config = configparser.ConfigParser()
            self.make_new()

    def verify(self):
        """Verify that a configuration file is valid."""
        for option in self.options:
            if not self.config.has_option("irc", option):
                print('Configuration file is invalid. Reconfiguring.')
                self.logger.info('Configuration file is invalid. Reconfiguring.')
                self.reconfigure()
        self.logger.info('Valid configuration file found.')

        # Allow reconfiguration even if the file is valid
        if not self.default:
            self.print_settings()
            reconfigure = ''
            while reconfigure != 'y' and reconfigure != 'n':
                reconfigure = input("Valid reconfiguration file found. Would you like to "
                                    "reconfigure? [Y/N] ").lower()
            if reconfigure == 'y':
                self.logger.debug('User has requested to reconfigure.')
                self.reconfigure()
