# Copyright (c) 2013 Molly White
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

import logging, os, pickle, queue, socket, threading
from command import Command
from configure import Configure
from executor import Executor
from time import time, sleep

class Bot(object):
    '''The Bot class is the core of the bot. It starts the IRC connection, and
    delegates tasks to other threads.'''
    
    def __init__(self, default, log_type, quiet):
        # Store command line settings
        self.default = default
        self.log_type = log_type
        self.quiet = quiet

        self.logger = logging.getLogger('GorillaBot')
        self.configuration = Configure( self.default, self.log_type, self.quiet )
        self.command_q = queue.Queue(100) # I'd be amazed if we hit 100 commands, but might as well set a limit
        self.response_q = queue.Queue(100)
        self.executor = Executor(self.command_q)
        
        self.channels = []  #List of currently-joined channels
        self.last_sent = 0
        self.last_received = time()
        self.last_ping_sent = time()
        self.running = False
        self.waiting_for_response = False
        self.numcodes = ['301', '311', '318', '353', '396', '401', '403', '433', '442', '470', '473']
        
        self.settings = self.configuration.get_configuration()
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.admin_commands, self.commands = self.load_commands()
        print(self.admin_commands)
        print(self.commands)
        self.start()
        
    def caffeinate(self):
        '''Make sure the connection stays open.'''
        now = time()
        if now - self.last_received > 150:
            if self.last_ping_sent < self.last_received:
                self.logger.info('Pinging server.')
                self.ping()
            elif now - self.last_ping_sent > 60:
                self.logger.warning('No ping response in 60 seconds. '
                                    'Shutting down.')
                self.shut_down()
   
    def connect(self):
        '''Connect to the IRC server.'''
        self.logger.debug('Thread created.')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        try:
            self.logger.info('Initiating connection.')
            self.socket.connect((self.settings['host'], self.settings['port']))
        except Exception:
            self.logger.error("Unable to connect to IRC server. Check your Internet "
                                  "connection.")
        else:
            self.send("NICK {0}".format(self.settings['nick']))
            self.send("USER {0} {1} * :{2}".format(self.settings['ident'],
                                                   self.settings['host'],
                                                   self.settings['realname']))
            self.private_message("NickServ", "ACC")
            self.loop()
    
    def dispatch(self, line):
        '''Determines the type of message received, creates a command object, adds it
        to the queue.'''
        self.logger.debug(line)
        
        if 'PING' in line[0]:
            command = Command(self, line, 'ping')
        elif 'NickServ' in line[0]:
            if self.waiting_for_response:
                self.response_q.put(line)
            command = Command(self, line, 'NickServ')
        elif len(line) > 1:
            if len(line[1]) == 3 and line[1].isdigit() and line[1] in self.numcodes:
                if self.waiting_for_response:
                    self.response_q.put(line[1])
                command = Command(self, line, 'numcode')
            elif line[1] == 'PRIVMSG':
                command = Command(self, line, 'message')
            else:
                return
        else:
            return
        
        # Add to the command queue to be executed
        if command.trigger:
            self.command_q.put(command)
    
    def join(self, channel_list):
        for channel in channel_list:
            if channel not in self.channels:
                self.logger.info('Joining {}.'.format(channel))
                self.send('JOIN ' + channel)
                self.channels.append(channel)
                
    def load_commands(self):
        try:
            with open(self.base_path + '/plugins/commands.pkl', 'rb') as admin_file:
                admin_commands = pickle.load(admin_file)
        except:
            admin_commands = None
        try:
            with open(self.base_path + '/plugins/admincommands.pkl', 'rb') as command_file:
                commands = pickle.load(command_file)
        except:
            commands = None
        return admin_commands, commands
        
    def loop(self):
        '''Main connection loop.'''
        self.running = True
        while True:
            try:
                buffer = ''
                buffer += str(self.receive())
            except socket.timeout:
                # No messages to deal with, move along
                pass
            except:
                # Something actually went wrong
                # TODO: Reconnect
                self.logger.exception("Unexpected socket error")
                self.running = False
                break
            else:
                self.last_received = time()
                list_of_lines = buffer.split('\\r\\n')
                for line in list_of_lines:
                    print(line)
                    line = line.strip().split()
                    self.dispatch(line)
            
            self.caffeinate()            
            
    def private_message(self, target, message, hide=False):
        '''Send a private message to a target on the server.'''
        for msg in self.split(message):
            self.send('PRIVMSG {0} :{1}'.format(target, msg))
            
    def receive(self, size=4096):
        '''Receive messages from the IRC server.'''
        return self.socket.recv(size)

    def send(self, message, hide=False):
        '''Send messages to the IRC server.'''
        time_since_send = time() - self.last_sent
        
        # Ensure messages aren't sent too quickly
        if time_since_send < 1:
            sleep(1-time_since_send)
        try:
            self.socket.sendall(bytes((message + '\r\n'), 'UTF-8'))
        except socket.error:
            # TODO: Reconnect
            self.running = False
            self.logger.error('Message ' + message + ' failed to send.')
        else:
            if not hide:
                self.logger.info('Sent: ' + message)
            self.last_sent = time()
    
    def shut_down(self):
        pass
            
    def split(self, message, maxlen=400, maxsplits=5):
        '''Split a message into smaller sections. Messages that are longer than
        maxlen*maxsplits will be truncated.'''
        splits = 0
        split_message = []
        while len(message) > 0 and splits < maxsplits:
            if len(message) > maxlen:
                split_message.append(message[:maxlen])
                message = message[maxlen:]
                splits+=1
            else:
                split_message.append(message)
                splits+=1
                break
        if splits >= maxsplits:
            self.logger.warning('Attempted to send a message that was too '
                                'long; message truncated.')
        return split_message

    def start(self):
        '''Begin the threads. The "IO" thread is the loop that receives commands from
        the IRC channels, and responds. The "Executor" thread is the thread used for
        simple commands that do not require threads of their own. More complex commands
        will create new threads as needed from this thread.'''
        threading.Thread(name='IO', target=self.connect).start()
        threading.Thread(name='Executor', target=self.executor.loop).start()