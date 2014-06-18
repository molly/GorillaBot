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

        self.last_message_sent = time()
        self.last_ping_sent = time()
        self.last_received = None
        self.logger = None
        self.settings = {}
        self.shutdown = threading.Event()
        self.response_lock = threading.Lock()
        self.socket = None
        self.message_q = queue.Queue()
        self.executor = Executor(self, self.message_q, self.shutdown)
        self.channels = []                  # Channels to which I'm joined
        self.opped_channels = []            # Channels in which I'm opped
        self.ops = []
        self.command_settings = {}
        self.header = {"User-Agent": "GorillaBot (https://github.com/molly/GorillaBot)"}
        self.users = {}

        # Initialize bot
        if not os.path.isdir(self.base_path + "/db"):
            os.makedirs(self.base_path + "/db")
        self.db_conn = sqlite3.connect(self.base_path + '/db/GorillaBot.db')
        self.admin_commands, self.commands = self.load_commands()
        self.initialize()

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
        try:
            self.logger.info('Initiating connection.')
            self.socket.connect((self.settings['host'], self.settings['port']))
        except OSError:
            self.logger.error("Unable to connect to IRC server. Check your Internet connection.")
        else:
            if self.settings['password']:
                self.send("PASS {0}".format(self.settings['password']), hide=True)
            self.send("NICK {0}".format(self.settings['nick']))
            self.send("USER {0} 0 * :{1}".format(self.settings['ident'], self.settings['realname']))
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
                if (line[2] == self.settings["nick"] or
                   line[3][1] == "!" or
                   line[3].startswith(":" + self.settings["nick"])):
                    message = Command(self, *line)
                else:
                    message = Privmsg(self, *line)
        if message:
            self.message_q.put(message)
        else:
            print(line)

    def initialize(self):
        """Initialize the bot. Parse command-line options, configure, and set up logging."""
        self.setup_logging()
        print('\n  ."`".'
              '\n / _=_ \\ \x1b[32m      __   __   __  . .   .     __   __   __  '
              '___\x1b[0m\n(,(oYo),) \x1b[32m    / _` /  \ |__) | |   |    |__| '
              '|__) /  \  |  \x1b[0m\n|   "   | \x1b[32m    \__| \__/ |  \ | |___'
              '|___ |  | |__) \__/  |  \x1b[0m \n \(\_/)/\n')
        start = Configurator(self.db_conn).configure()
        print(start)
        if start:
            # self.start()
            pass
        else:
            return

    def join(self, chans=None):
        """Join the given channel, list of channels, or if no channel is specified, join any
        channels that exist in the config but are not already joined."""
        if chans is None:
            chans = self.settings["chans"]
        if type(chans) is str:
            chans = [chans]
        if type(chans) is list:
            for chan in chans:
                if chan in self.channels:
                    self.logger.info("Already in channel {0}. Not joining.".format(chan))
                else:
                    self.logger.info("Joining {0}.".format(chan))
                    self.send('JOIN ' + chan)
                    self.channels.append(chan)

    def load_commands(self):
            try:
                with open(self.base_path + '/plugins/commands.pkl', 'rb') as admin_file:
                    admin_commands = pickle.load(admin_file)
            except OSError:
                admin_commands = None
            try:
                with open(self.base_path + '/plugins/admincommands.pkl', 'rb') as command_file:
                    commands = pickle.load(command_file)
            except OSError:
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
        self.logger.debug("Pinging {}.".format(self.settings['host']))
        self.send('PING {}'.format(self.settings['host']))

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
            self.socket.sendall(bytes((message + "\r\n"), "utf-8"))
        except socket.error:
            self.shutdown.set()
            self.logger.error("Message '" + message + "' failed to send. Shutting down.")
        else:
            if not hide:
                self.logger.debug("Sent message: " + message)
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
