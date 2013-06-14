# Copyright (c) 2013 Molly White
# Portions copyright (c) 2009-2013 Ben Kurtovic <ben.kurtovic@verizon.net>
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

import logging, socket, os
from getpass import getpass
from time import sleep, time

__all__ = ["Connection"]

class Connection(object):
    '''Performs the connection to the IRC server and communicates with it.'''
    
    def __init__(self, bot, host, port, nick, ident, realname, chans, botop):
        '''Constructs the connection object. Sets up logging.'''
        self._bot = bot
        self._host = host
        self._port = port
        self._nick = nick
        self._ident = ident
        self._realname = realname
        self._chans = chans
        self.admins = botop
        self._password = None
        self._commands = None
        self.logger = logging.getLogger("GorillaBot")
        
        self._last_sent = 0
        self._last_ping_sent = time()
        self._last_received = time()
        self._notify_check = time()
        
        self._running = False
        self._reconnect_tries = 0 # Number of times the bot has auto-reconnected
        self._try_reconnect = True
        
    def __repr__(self):
        '''Return the not-so-pretty representation of Connection.'''
        rep = "Connection: host={0!r}, port={1!r}, nick={2!r}, ident={3!r}, "
        "realname={4!r}, channel={5!r}, botop={6!r}"
        return rep.format(self._host, self._port, self._nick, self._ident, self._realname,
                          self._chans, self.admins)
    
    def __str__(self):
        '''Return somewhat prettier representation of Connection.'''
        rep = "{0} is joining {1} on {2} on port {3}."
        return rep.format(self._nick, self._chans, self._host, self._port)
    
    def _close(self, retry = False):
        '''End connection with IRC server, close socket.'''
        self._running = False
        if not retry:
            self._try_reconnect = False
        self.logger.info("Closing.")
        try:
            self._socket.shutdown(socket.SHUT_RDWR) # Shut down before close
        except socket.error:
            pass #Socket is already closed
        self._socket.close()
    
    def _connect(self):
        '''Connect to the IRC server.'''
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(5)
        try:
            self._socket.connect((self._host, self._port))
        except Exception:
            self.logger.exception("Unable to connect to IRC server. Check your Internet "
                                  "connection.")
        else:
            self._send("NICK {0}".format(self._nick))
            self._send("USER {0} {1} * :{2}".format(self._ident, self._host, self._realname))
            self.private_message("NickServ", "ACC")
            self.loop()
            
    def _receive(self, size=4096):
        '''Receive messages from the IRC server.'''
        message = self._socket.recv(size)
        return message
    
    def _reconnect(self):
        if self._reconnect_tries < 5 and self._try_reconnect == True:
            self.logger.debug("Attempting to reconnect ({} earlier tries)."
                              .format(self._reconnect_tries))
            sleep(5)
            self._connect()
            self._reconnect_tries += 1
        
    def _send(self, message, hide=False):
        '''Send messages to the IRC server.'''
        time_since_send = time() - self._last_sent
        if time_since_send < 1:
            sleep(1-time_since_send)
        try:
            self._socket.sendall(bytes((message + "\r\n"), 'UTF-8'))
        except socket.error:
            self._running = False
            self._reconnect()
            self.logger.exception("Message " + message + " failed to send.")
        else:
            if not hide:
                self.logger.info("Sent message: " + message)
            self._last_sent = time()
            
    def _split(self, msgs, maxlen=400, maxsplits=5):
        """Split a large message into multiple messages smaller than maxlen."""
        words = msgs.split(" ")
        splits = 0
        while words and splits < maxsplits:
            splits += 1
            if len(words[0]) > maxlen:
                word = words.pop(0)
                yield word[:maxlen]
                words.insert(0, word[maxlen:])
            else:
                msg = []
                while words and len(" ".join(msg + [words[0]])) <= maxlen:
                    msg.append(words.pop(0))
                yield " ".join(msg)          
    
    def caffeinate(self):
        '''Keep the connection open.'''
        now = time()
        if now - self._last_received > 150:
            if self._last_ping_sent < self._last_received:
                self.logger.info("Pinging server.")
                self.ping()
            elif now - self._last_ping_sent > 60:
                self.logger.info("No ping response in 60 seconds.")
                self.shut_down(True)
            
    def dispatch(self, line):
        '''Process lines received.'''
        self._last_received = time()
        self._bot.dispatch(line)      
        
    def join(self, chan=None):   
        '''Join a channel.'''
        if chan:
            self.logger.info("Joining {}.".format(chan))
            self._send("JOIN {}".format(chan))
            self._chans.append(chan)
        else:
            for chan in self._chans:
                self.logger.info("Joining {}.".format(chan))
                self._send("JOIN {}".format(chan))
                
    def loop(self):
        '''Main connection loop.'''
        buffer = ''
        self._running = True
        while True:
            try:
                buffer += str(self._receive())
            except socket.timeout:
                pass
            except Exception:
                self._running = False
                self._reconnect()
                break
            else:
                list_of_lines = buffer.split("\\r\\n")
                buffer = list_of_lines.pop()
                for line in list_of_lines:
                    line = line.strip().split()
#                    print(line)
                    self.dispatch(line)
            finally:
                if not self._running:
                    self._reconnect()
                    break
                if time() - self._notify_check >= 10:
                    # Perform a check on notified people every 5 minutes
                    self._bot.GorillaCommander.stalker._update(self._bot)
                    self._notify_check = time()
                
                self.caffeinate()
            
    def me(self, message, channel):
        '''Say an action to the channel.'''
        self.say("\x01ACTION {0}\x01".format(message), channel)
            
    def nickserv_identify(self):
        '''Prompt the user to enter their password, then identify to NickServ.'''
        if not self._password:
            self._tentative_password = getpass("NickServ password: ")
            self.private_message("NickServ", "IDENTIFY {0} {1}"
                                 .format(self._nick, self._tentative_password), True)
        else:
            self.private_message("NickServ", "IDENTIFY {0} {1}".format(self._nick, self._password),
                                 True)

    def part(self, chan, remove_only=False):
        '''Part from an IRC channel.'''
        if remove_only:
            self._chans.remove(chan)
        else:
            if chan[0] == "#" and chan in self._chans:
                self.logger.info("Parting from {}.".format(chan))
                self._send("PART {}".format(chan))
                self._chans.remove(chan)
            
    def ping(self):
        '''Ping the host server.'''
        self._last_ping_sent = time()
        self.logger.debug("Pinging host.")
        self._send("PING {}".format(self._host), True)
        
    def pong(self, server):
        '''Sends a pong reply.'''
        self.logger.debug("Ponging {}".format(server))
        self._send("PONG {}".format(server), True)
        
    def private_message(self, target, message, hide=False):
        '''Send a private message to a target on the server.'''
        for msg in self._split(message, 400):
            privmsg = "PRIVMSG {0} :{1}".format(target, msg)
            self._send(privmsg, hide)
              
    def quit(self):
        '''Disconnect from the server.'''
        self._send("QUIT")
            
    def say(self, message, channel):
        '''Say something to the channel or in a private message to the user
        that sent a command.'''
        self.private_message(channel, message)
        
    def shut_down(self, retry=False):
        '''Gracefully shuts down.'''
        self.logger.info("Shutting down.")
        self.quit()
        self._close(retry)
        
    def whois(self, nick):
        self._send("WHOIS {0}".format(nick))
