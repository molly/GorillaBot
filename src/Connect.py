'''
Created on Feb 4, 2013

@author: mollywhite
'''
import socket
from time import sleep

__all__ = ["Connection"]

class Connection(object):
    def __init__(self):
        self._host = "irc.freenode.net"
        self._port = 6667
        self._nick = "GorillaBot"
        self._ident = "GorillaBot"
        self._realname = "GorillaBot"
        self._password = "temp"
        
    def __repr__(self):
        '''Return the not-so-pretty representation of Connection.'''
        rep = "Connection: host={0!r}, port={1!r}, nick={2!r}, ident={3!r}, realname={4!r}"
        return rep.format(self.host, self.port, self.nick, self.ident, self.realname)
    
    def __str__(self):
        '''Return somewhat prettier reperesentation of Connection.'''
        rep = "{0} is joining {1} on port {2}."
        return rep.format(self.nick, self.host, self.port)
    
    def _connect(self):
        '''Connect to the IRC server.'''
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect(self.host, self.port)
        except socket.error:
            sleep(5)
            self._connect()
        self._send("NICK {}".format(self.nick))
        self._send("USER {} {} * :{}".format(self.ident, self.host, self.realname))