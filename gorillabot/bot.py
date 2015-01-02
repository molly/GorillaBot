#!/usr/bin/env python3
#
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

from configure import Configurator
from executor import Executor
import logging
from logging import handlers
from message import *
import os
import pickle
import queue
import re
import socket
import sqlite3
import threading
from time import sleep, strftime, time


class Bot(object):
    """The core of the IRC bot. It maintains the IRC connection, and delegates other tasks."""

    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.log_path = self.base_path + '/logs'

        self.configuration = None
        self.last_message_sent = time()
        self.last_ping_sent = time()
        self.last_received = None
        self.logger = None
        self.shutdown = threading.Event()
        self.response_lock = threading.Lock()
        self.socket = None
        self.message_q = queue.Queue()
        self.executor = Executor(self, self.message_q, self.shutdown)
        self.header = {"User-Agent": "GorillaBot (https://github.com/molly/GorillaBot)"}

        self.initialize()

    def action(self, target, message):
        """Perform an action to target on the server."""
        self.private_message(target, "\x01ACTION " + message + "\x01")

    def caffeinate(self):
        """Make sure the connection stays open."""
        now = time()
        if now - self.last_received > 150:
            if self.last_ping_sent < self.last_received:
                self.ping()
            elif now - self.last_received > 60:
                self.logger.warning('No ping response in 60 seconds. Shutting down.')
                self.shutdown.set()

    def connect(self):
        """Connect to the IRC server."""
        self.logger.debug('Thread created.')
        self.socket = socket.socket()
        self.socket.settimeout(5)
        cursor = self.db_conn.cursor()
        cursor.execute('''SELECT * FROM configs WHERE name = ?''', (self.configuration,))
        data = cursor.fetchone()
        cursor.close()
        name, nick, realname, ident, password, youtube, forecast = data
        try:
            self.logger.info('Initiating connection.')
            self.socket.connect(("chat.freenode.net", 6667))
        except OSError:
            self.logger.error("Unable to connect to IRC server. Check your Internet connection.")
            self.shutdown.set()
        else:
            if password:
                self.send("PASS {0}".format(password), hide=True)
            self.send("NICK {0}".format(nick))
            self.send("USER {0} 0 * :{1}".format(ident, realname))
            self.private_message("NickServ", "ACC")
            self.loop()

    def dispatch(self, line):
        """Inspect this line and determine if further processing is necessary."""
        length = len(line)
        message = None
        if length <= 2:
            if line[0] == "PING":
                message = Ping(self, *line)
        if length >= 2:
            if line[1] == "PONG":
                message = Ping(self, *line)
            elif line[1].isdigit():
                message = Numeric(self, *line)
            elif line[1] == "NOTICE":
                message = Notice(self, *line)
            elif line[1] in ["MODE", "JOIN", "PART"]:
                message = Operation(self, *line)
            elif line[1] == "PRIVMSG":
                nick = self.get_config("nick")
                if (length >= 3 and line[2] == nick) or (length >= 4 and (
                    line[3].startswith(":!") or line[3].startswith(":" + nick))):
                    message = Command(self, *line)
                else:
                    message = Privmsg(self, *line)
        if message:
            self.message_q.put(message)
        else:
            print(line)

    def get_chan_id(self, channel):
        '''Get the chan_id for the given channel.'''
        cursor = self.db_conn.cursor()
        cursor.execute('''SELECT chan_id FROM channels WHERE name = ? and config = ?''',
                       (channel, self.configuration))
        data = cursor.fetchone()
        cursor.close()
        if data is None:
            return data
        else:
            return data[0]

    def get_config(self, config):
        """Retrieve the given configuration setting from the database."""
        cursor = self.db_conn.cursor()
        query = '''SELECT %s FROM configs WHERE name = ?''' % config
        cursor.execute(query, (self.configuration,))
        value = cursor.fetchone()
        cursor.close()
        return value[0] if value else None

    def get_setting(self, setting, chan):
        """Retrieve the given setting from the database."""
        chan_id = self.get_chan_id(chan)
        if chan_id is None:
            return False
        cursor = self.db_conn.cursor()
        cursor.execute('''SELECT value FROM settings WHERE chan_id = ? AND setting = ?''',
                       (chan_id, setting))
        data = cursor.fetchone()
        cursor.close()
        return data[0] if data else None

    def initialize(self):
        """Initialize the bot. Parse command-line options, configure, and set up logging."""
        if not os.path.isdir(self.base_path + "/db"):
            os.makedirs(self.base_path + "/db")
        self.db_conn = sqlite3.connect(self.base_path + '/db/GorillaBot.db',
                                       check_same_thread=False)
        self.db_conn.execute('''PRAGMA foreign_keys = ON''')
        self.admin_commands, self.commands = self.load_commands()
        self.setup_logging()
        print('\n  ."`".'
              '\n / _=_ \\ \x1b[32m    __   __   __  . .   .    __   __   __  '
              '___\x1b[0m\n(,(oYo),) \x1b[32m  / _` /  \ |__) | |   |   |__| '
              '|__) /  \  |  \x1b[0m\n|   "   | \x1b[32m  \__| \__/ |  \ | |__ '
              '|__ |  | |__) \__/  |  \x1b[0m \n \(\_/)/\n')
        try:
            self.configuration = Configurator(self.db_conn).configure()
        except KeyboardInterrupt:
            self.logger.info("Caught KeyboardInterrupt. Shutting down.")
        if self.configuration:
            self.start()
        else:
            return

    def join(self, chans=None):
        """Join the given channel, list of channels, or if no channel is specified, join any
        channels
        that exist in the config but are not already joined."""
        if chans is None:
            cursor = self.db_conn.cursor()
            cursor.execute('''SELECT name, joined FROM channels WHERE config = ?''',
                           (self.configuration,))
            data = cursor.fetchall()
            cursor.close()
            for row in data:
                if row[1] == 0:
                    self.logger.info("Joining {0}.".format(row[0]))
                    self.send('JOIN ' + row[0])
                    cursor = self.db_conn.cursor()
                    cursor.execute(
                        '''UPDATE channels SET joined = 1 WHERE name = ? AND config = ?''',
                        (row[0], self.configuration))
                    self.db_conn.commit()
                    cursor.close()
        else:
            if type(chans) is str:
                chans = [chans]
            for chan in chans:
                self.logger.info("Joining {0}.".format(chan))
                self.send('JOIN ' + chan)
                cursor = self.db_conn.cursor()
                cursor.execute('''UPDATE channels SET joined = 1 WHERE name = ?''', (chan,))
                if cursor.rowcount < 1:
                    cursor.execute('''INSERT INTO channels VALUES (NULL, ?, 1, ?)''',
                                   (chan, self.configuration))
                self.db_conn.commit()
                cursor.close()

    def load_commands(self):
        try:
            with open(self.base_path + '/plugins/commands.pkl', 'rb') as admin_file:
                admin_commands = pickle.load(admin_file)
        except (OSError, IOError):
            admin_commands = None
        try:
            with open(self.base_path + '/plugins/admincommands.pkl', 'rb') as command_file:
                commands = pickle.load(command_file)
        except (OSError, IOError):
            commands = None
        return admin_commands, commands

    def loop(self):
        """Main connection loop."""
        while not self.shutdown.is_set():
            try:
                buffer = ''
                buffer += str(self.socket.recv(4096))
            except socket.timeout:
                # No messages to deal with, move along
                pass
            except IOError:
                # Something actually went wrong
                # TODO: Reconnect
                self.logger.exception("Unexpected socket error")
                break
            else:
                self.last_received = time()
                if buffer.startswith("b'"):
                    buffer = buffer[2:]
                if buffer.endswith("'"):
                    buffer = buffer[:-1]
                list_of_lines = buffer.split('\\r\\n')
                list_of_lines = filter(None, list_of_lines)
                for line in list_of_lines:
                    line = line.strip().split()
                    if line != "":
                        self.dispatch(line)
            self.caffeinate()
        self.socket.close()

    def parse_hostmask(self, nick):
        """Parse out the parts of the hostmask."""
        m = re.match(':?(?P<nick>.*?)!~?(?P<user>.*?)@(?P<host>.*)', nick)
        if m:
            return {"nick": m.group("nick"), "user": m.group("user"), "host": m.group("host")}
        else:
            return None

    def ping(self):
        """Send a ping to the server."""
        self.logger.debug("Pinging chat.freenode.net.")
        self.send("PING chat.freenode.net")

    def pong(self, server):
        """Respond to a ping from the server."""
        self.logger.debug("Ponging {}.".format(server))
        self.send('PONG {}'.format(server))

    def private_message(self, target, message, hide=False):
        """Send a private message to a target on the server."""
        self.send('PRIVMSG {0} :{1}'.format(target, message), hide)

    def send(self, message, hide=False):
        """Send message to the server."""
        if (time() - self.last_message_sent) < 1:
            sleep(1)
        try:
            message = re.sub(r'(\n|\r)', "", message)
            self.socket.sendall(bytes((message[:510] + "\r\n"), "utf-8"))
        except socket.error:
            self.shutdown.set()
            self.logger.error("Message '" + message + "' failed to send. Shutting down.")
        else:
            if not hide:
                self.logger.debug("Sent: " + message)
            self.last_message_sent = time()

    def setup_logging(self):
        """Set up logging to a logfile and the console."""
        self.logger = logging.getLogger('GorillaBot')

        # Set logging level
        self.logger.setLevel(logging.DEBUG)

        # Create the file logger
        file_formatter = logging.Formatter(
            "%(asctime)s - %(filename)s - %(threadName)s - %(levelname)s : %(message)s")
        if not os.path.isdir(self.log_path):
            os.mkdir(self.log_path)
        logname = (self.log_path + "/{0}.log").format(strftime("%H%M_%m%d%y"))
        # Files are saved in the logs sub-directory as HHMM_mmddyy.log
        # This log file rolls over every seven days.
        filehandler = logging.handlers.TimedRotatingFileHandler(logname, 'd', 7)
        filehandler.setFormatter(file_formatter)
        filehandler.setLevel(logging.INFO)
        self.logger.addHandler(filehandler)
        self.logger.info("File logger created; saving logs to {}.".format(logname))

        # Create the console logger
        console_formatter = logging.Formatter(
            "%(asctime)s - %(threadName)s - %(levelname)s: %(message)s", datefmt="%I:%M:%S %p")
        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(console_formatter)

        self.logger.addHandler(consolehandler)
        self.logger.info("Console logger created.")

    def start(self):
        """Begin the threads. The "IO" thread is the loop that receives commands from the IRC
        channels, and responds. The "Executor" thread is the thread used for simple commands
        that do not require threads of their own. More complex commands will create new threads
        as needed from this thread. """
        try:
            io_thread = threading.Thread(name='IO', target=self.connect)
            io_thread.start()
            threading.Thread(name='Executor', target=self.executor.loop).start()
            while io_thread.isAlive():
                io_thread.join(1)
        except KeyboardInterrupt:
            self.logger.info("Caught KeyboardInterrupt. Shutting down.")
            self.shutdown.set()
            self.db_conn.close()


if __name__ == "__main__":
    bot = Bot()
