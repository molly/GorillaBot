#!/usr/bin/env python3
#
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

from configure import Configurator
from executor import Executor
import json
import logging
from logging import handlers
from message import *
import os
import pickle
import queue
import re
import socket
import threading
from time import sleep, strftime, time


class Bot(object):
    """The core of the IRC bot. It maintains the IRC connection, and delegates other tasks."""

    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.abspath(os.path.join(self.base_path, "..", "config.json"))
        self.log_path = os.path.abspath(os.path.join(self.base_path, 'logs'))

        self.configuration = None
        self.configuration_name = None
        self.last_message_sent = time()
        self.last_ping_sent = time()
        self.last_received = None
        self.last_reconnect = None
        self.logger = None
        self.shutdown = threading.Event()
        self.shutdown_message = None
        self.reconnect_time = 5                   # Seconds to wait before reconnecting, or none to not reconnect
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
                self.shutdown_message = 'No ping response in 60 seconds.'
                self.shutdown.set()

    def connect(self):
        """Connect to the IRC server."""
        self.logger.debug('Thread created.')
        self.socket = socket.socket()
        self.socket.settimeout(5)
        try:
            self.logger.info('Initiating connection.')
            self.socket.connect(("chat.freenode.net", 6667))
        except OSError:
            self.logger.error("Unable to connect to IRC server. Check your Internet connection.")
            self.shutdown.set()
            self.maybe_reconnect()
        else:
            if self.configuration["password"]:
                self.send("PASS {0}".format(self.configuration["password"]), hide=True)
            self.send("NICK {0}".format(self.configuration["nick"]))
            self.send("USER {0} 0 * :{1}".format(self.configuration["ident"],
                                                 self.configuration["realname"]))
            self.private_message("NickServ", "ACC")
            self.loop()

    def dispatch(self, line):
        """Inspect this line and determine if further processing is necessary."""
        length = len(line)
        message = None
        if 2 >= length >= 1:
            if line[0] == "PING":
                message = Ping(self, *line)
        if length >= 2:
            if line[1] == "PONG":
                message = Ping(self, *line)
            elif line[1].isdigit():
                message = Numeric(self, *line)
            elif line[1] == "NOTICE":
                message = Notice(self, *line)
            elif line[1] == "PRIVMSG":
                nick = self.configuration["nick"]
                if (length >= 3 and line[2] == nick) or (length >= 4 and (
                    line[3].startswith(":!") or line[3].startswith(":" + nick))):
                    message = Command(self, *line)
                else:
                    message = Privmsg(self, *line)
        if message:
            self.message_q.put(message)
        else:
            print(line)

    def get_admin(self, nick=None):
        """Get the hostnames for the bot admins. If nick is supplied, add that user as an admin."""
        botops = self.configuration["botops"]
        if nick:
            ops = [nick]
        else:
            ops = botops.keys()
        self.response_lock.acquire()
        ignored_messages = []
        for op in ops:
            self.send("WHOIS " + op)
            while True:
                try:
                    msg = self.message_q.get(True, 120)
                except queue.Empty:
                    self.logger.error("No response while getting admins. Shutting down.")
                    self.shutdown.set()
                    break
                else:
                    if type(msg) is Numeric:
                        if msg.number == '311':
                            # User info
                            line = msg.body.split()
                            botops.update({op: {"user": line[1], "host": line[2]}})
                            self.logger.info(
                                "Adding {0} {1} to bot ops".format(line[1], line[2],))
                            break
                        elif msg.number == '318':
                            # End of WHOIS
                            break
                        elif msg.number == '401':
                            # No such user
                            self.logger.info("No user {0} logged in.".format(op))
                            break
                    ignored_messages.append(msg)
        self.response_lock.release()
        for msg in ignored_messages:
            self.message_q.put(msg)
        self.configuration["botops"] = botops
        self.update_configuration(self.configuration)

    def get_configuration(self):
        """Get the configuration dict for the active configuration."""
        with open(self.config_path, 'r') as f:
            blob = json.load(f)
        return blob[self.configuration_name]

    def get_setting(self, setting, chan):
        """Get the value of the given setting for the given channel."""
        if chan not in self.configuration["chans"]:
            self.logger.warning("Tried to get settings for nonexistant channel {}.".format(chan))
            return None
        if setting not in self.configuration["chans"][chan]["settings"]:
            return None
        return self.configuration["chans"][chan]["settings"][setting]

    def initialize(self):
        """Initialize the bot. Parse command-line options, configure, and set up logging."""
        self.admin_commands, self.commands = self.load_commands()
        self.setup_logging()
        print('\n  ."`".'
              '\n / _=_ \\ \x1b[32m    __   __   __  . .   .    __   __   __  '
              '___\x1b[0m\n(,(oYo),) \x1b[32m  / _` /  \ |__) | |   |   |__| '
              '|__) /  \  |  \x1b[0m\n|   "   | \x1b[32m  \__| \__/ |  \ | |__ '
              '|__ |  | |__) \__/  |  \x1b[0m \n \(\_/)/\n')
        try:
            self.configuration_name = Configurator().configure()
            self.configuration = self.get_configuration()
        except KeyboardInterrupt:
            self.logger.info("Caught KeyboardInterrupt. Shutting down.")
        self.start()

    def is_admin(self, user):
        """Check if user is a bot admin."""
        botops = self.configuration["botops"].keys()
        mask = self.parse_hostmask(user)
        for op in botops:
            op_info = self.configuration["botops"][op]
            if op_info["host"] == mask["host"]:
                return True
            elif op == mask["nick"]:
                # User is on the list of ops, but wasn't joined when the bot entered
                self.get_admin(op)
                return True
        return False

    def join(self, chans=None):
        """Join the given channel, list of channels, or if no channel is specified, join any
        channels that exist in the config but are not already joined."""
        if chans is None:
            chans = self.configuration["chans"]
            if chans:
                for chan in chans.keys():
                    if not chans[chan]["joined"]:
                        self.logger.info("Joining {0}.".format(chan))
                        self.send('JOIN ' + chan)
                        self.configuration["chans"][chan]["joined"] = True
        else:
            for chan in chans:
                self.logger.info("Joining {0}.".format(chan))
                self.send('JOIN ' + chan)
                self.configuration["chans"].update({chan: {"joined": True, "settings": {}}})
        self.update_configuration(self.configuration)

    def load_commands(self):
        """Load commands from the pickle files if they exist."""
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
        self.send("QUIT :" + self.shutdown_message if self.shutdown_message else "")
        self.maybe_reconnect()

    def maybe_reconnect(self):
        if not self.reconnect_time:
            self.socket.close()
            return
        elif self.reconnect_time > 600:
            # Backing off isn't helping; stop trying
            self.reconnect_time = None
            self.logger.info("Stopping reconnect attempts after too many tries.")
            self.socket.close()
            return

        if self.last_reconnect and time() - self.last_reconnect < 600:
            # Back off if the last reconnect was within the past 10 min
            self.reconnect_time = self.reconnect_time * 3
        else:
            # Reset reconnect time if we haven't tried to reconnect lately
            self.reconnect_time = 5
        self.logger.info("Waiting " + str(self.reconnect_time) + " seconds and then attempting to reconnect.")
        sleep(self.reconnect_time)
        self.last_reconnect = time()
        self.shutdown_message = None
        self.shutdown.clear()
        self.start()

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
        self.last_ping_sent = time()

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
            self.shutdown_message = "Send failed."
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
            self.shutdown_message = 'Shut down from command line.'
            self.reconnect_time = None
            self.shutdown.set()

    def update_configuration(self, updated_configuration):
        """Update the full configuration blob with the new settings, then write it to the file.
        Also updates the stored self.configuration dict."""
        with open(self.config_path, 'r') as f:
            blob = json.load(f)
        updated_configuration = {self.configuration_name: updated_configuration}
        if blob:
            blob.update(updated_configuration)
        else:
            blob = updated_configuration
        with open(self.config_path, "w") as f:
            json.dump(blob, f, indent=4)
        self.configuration = blob[self.configuration_name]

if __name__ == "__main__":
    bot = Bot()
