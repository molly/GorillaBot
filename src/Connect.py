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

import socket
import logging
from getpass import getpass
from time import sleep, time

__all__ = ["Connection"]

class Connection(object):
    '''Performs the connection to the IRC server.'''
    
    def __init__(self, host, port, nick, ident, realname, chans):
        self._host = host
        self._port = port
        self._nick = nick
        self._ident = ident
        self._realname = realname
        self._password = getpass()
        self._chans = chans
        self.logger = logging.getLogger("GorillaBot")
        
        self._last_sent = 0
        self._last_ping_sent = time()
        self._last_received = time()
        
        self._fine_and_dandy = True # Status of the socket connection
        
    def __repr__(self):
        '''Return the not-so-pretty representation of Connection.'''
        rep = "Connection: host={0!r}, port={1!r}, nick={2!r}, ident={3!r}, "
        "realname={4!r}, password={5!r}, channel={6!r}"
        return rep.format(self.host, self.port, self.nick, self.ident, self.realname,
                          self.password, self.chan)
    
    def __str__(self):
        '''Return somewhat prettier representation of Connection.'''
        rep = "{0} is joining {1} on {2} on port {3}."
        return rep.format(self.nick, self.channel, self.host, self.port)
    
    def _close(self):
        '''End connection with IRC server, close socket.'''
        self.logger.info("Closing.")
        self._socket.shutdown(socket.SHUT_RDWR) # Shut down before close
        self._socket.close()
    
    def _connect(self):
        '''Connect to the IRC server.'''
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect(self.host, self.port)
        except socket.error:
            self.logger.exception("Unable to connect to IRC server. Retrying...")
            sleep(5) #Wait 5 seconds before retrying
            self._connect()
            
        joinlist = ",".join(self.chans)
        
        self._send("NICK {}".format(self.nick))
        self.logger.info("Setting nick: {}".format(self.nick))
        self._send("USER {0} {1} * :{2}".format(self.ident, self.host,
                                                self.realname))
        self.logger.info("Authing. Ident: {0}, Host: {1}, Real name: {2}"
                          .format(self.ident, self.host, self.realname))
        self._send("JOIN {0}".format(joinlist))
        self.logger.info("Joining channels: {}".format(joinlist))
            
    def _part(self, chans, message=None):
        '''Part one or more IRC channels (with optional message).'''
        partlist = ",".join(chans)
        if message:
            self._send("PART {0} {1}".format(partlist, message))
        else:
            self._send("PART {}".format(partlist))
            
    def _dispatch(self, line):
        '''Process lines received.'''
        if line[0] == "PING": # Pong back if a ping message is received
            self.pong(line[1][1:])
            
    def _quit(self, message=None):
        '''Disconnect from the server (with optional quit message).'''
        if message:
            self._send("QUIT: {}".format(message))
        else:
            self._send("QUIT")
            
    def _receive(self, size=4096):
        '''Receive messages from the IRC server.'''
        message = self._socket.recv(size)
        if not message:
            raise socket.error(0, "Socket connection broken.")
            self._fine_and_dandy = False
        return message
        
    def _send(self, message):
        '''Send messages to the IRC server.'''
        time_since_send = time() - self.last_sent
        if time_since_send < 1:
            sleep(1-time_since_send)
        try:
            self.socket.sendall(message + "\r\n")
        except socket.error:
            self._fine_and_dandy = False
            self.logger.exception(message + "failed to send.")
        else:
            self.logger.info(message)
            self._last_sent = time()
            
    @property
    def host(self):
        '''Hostname of the server (e.g., "irc.freenode.net")'''
        return self._host
    
    @property
    def port(self):
        '''Port on which we are connecting (e.g., 6667)'''
        return self._port
    
    @property
    def nick(self):
        '''Nickname of the bot (e.g., GorillaBot)'''
        return self._nick
    
    @property
    def ident(self):
        '''Ident on the server (e.g., GorillaBot)'''
        return self._ident
    
    @property
    def realname(self):
        '''Real name (as would be displayed in WHOIS, e.g. GorillaBot)'''
        return self._realname
    
    @property
    def password(self):
        '''Password for identifying to services'''
        return self._password
    
    @property
    def chans(self):
        '''List of channels to join (e.g., "#wikipedia-en")'''
        return self._chans
    
    def caffeinate(self):
        '''Keep the connection open.'''
        now = time()
        if now - self._last_received > 150:
            if self._last_ping_sent > self._last_received:
                self.logger.info("Pinging server.")
                self.ping()
            elif self._last_ping_sent > 60:
                self.logger.info("No ping response in 60 seconds.")
                self._quit()
                self._close()
            
    
    def loop(self):
        '''Main connection loop.'''
        buffer = ''
        while True:
            try:
                buffer += self._receive()
            except socket.error:
                break
            list_of_lines = buffer.split("\n")
            for line in list_of_lines:
                line.strip().split()
            if not self._fine_and_dandy:
                break
            
    def ping(self):
        '''Ping the host server.'''
        self._last_ping_sent = time()
        self._send("PING {}".format(self.host))
        
    def pong(self, server):
        self._send("PONG {}".format(server))
