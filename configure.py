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

import configparser, logging, os
from logging import handlers
from time import strftime

class Configure(object):
    '''Deals with the configuration file. It will create a new one if one doesn't
    exist, or find or modify an existing one.'''
    
    def __init__(self, default, log_type, quiet):
        self.config = configparser.ConfigParser()
        self.config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
        self.log_path = os.path.dirname(os.path.abspath(__file__)) + '/logs'
        self.default = default
        self.log_type = log_type
        self.quiet = quiet
        self.options = ('host', 'port', 'nick', 'ident', 'realname', 'chans', 'botop',
                         'fullop')
        
        self.setup_logging()
        self.load()
        
    def get_configuration(self):
        '''Return configuration as a dictionary.'''
        host = self.config.get("irc", "Host")
        port = int(self.config.get("irc", "Port"))
        nick = self.config.get("irc", "Nick")
        realname = self.config.get("irc", "Realname")
        ident = self.config.get("irc", "Ident")
        chans = self.config.get("irc", "Chans")
        botop = self.config.get("irc", "Botop")
        fullop = self.config.get("irc", "Fullop")
        
        # Allow comma- or space-separated lists
        if ',' in chans:
            chanlist = chans.split(',')
        else:
            chanlist = chans.split(' ')
        for i in range(len(chanlist)):
            chanlist[i] = chanlist[i].strip()
        
        if ',' in botop:
            oplist = botop.split(',')
        else:
            oplist = botop.split(' ')
        for i in range(len(oplist)):
            oplist[i] = oplist[i].strip()
            
        configuration = {"host":host, "port":port, "nick":nick,"realname":realname,
                         "ident":ident, "chans":chanlist, "botop":oplist, "fullop":fullop}
        
        return configuration
        
    def load(self):
        '''Try to load an existing configuration file. If it exists, validate it. If
        it does not, begin to create a new one.'''
        try:
            self.config.read_file(open(self.config_path))
        except IOError:
            # File doesn't exist; create new one.
            self.logger.info('Unable to open {}. Creating a new configuration file.'
                             .format(self.config_path))
            self.make_new()
        else:
            # File exists; make sure it's properly formatted
            self.verify()
            
    def make_new(self):
        '''Create a new configuration file from scratch.'''
        verify = ''
        while verify != 'y':
            print('\n')
            host = self.prompt("Host", "irc.freenode.net")
            port = self.prompt("Port", 6667)
            nick = self.prompt("Nick", "GorillaBot")
            realname = self.prompt("Ident", "GorillaBot")
            ident = self.prompt("Realname", "GorillaBot")
            chans = self.prompt("Chans")
            botop = self.prompt("Bot operator(s)")
            print("------------------------------\n Host: {0}\n Port: {1}\n Nickname: "
              "{2}\n Real name: {3}\n Identifier: {4}\n Channels:"
              " {5}\n Bot operator(s): {6}\n------------------------------".format(host, port, nick,
                                                            realname, ident, chans, botop))
            
            while verify != 'y' and verify != 'n':
                verify = input('Is this configuration correct? [Y/N]: ')
                verify = verify.lower()
                
        self.config.add_section("irc")
        self.config.set("irc", "host", host)
        self.config.set("irc", "port", str(port))
        self.config.set("irc", "nick", nick)
        self.config.set("irc", "realname", realname)
        self.config.set("irc", "ident", ident)
        self.config.set("irc", "chans", chans)
        self.config.set("irc", "botop", botop)
        self.config.set("irc", "fullop", '[]')
        
        with open(self.config_path, 'w') as config_file:
            self.config.write( config_file )
            
        self.logger.info( "Configuration file saved.")
        
    def print_settings(self):
        '''Display existing settings in a configuration file.'''
        host = self.config.get("irc", "host")
        port = self.config.get("irc", "port")
        nick = self.config.get("irc", "nick")
        realname = self.config.get("irc", "realname")
        ident = self.config.get("irc", "ident")
        chans = self.config.get("irc", "chans")
        botop = self.config.get("irc", "botop")
        print("------------------------------\n Host: {0}\n Port: {1}\n Nickname: "
              "{2}\n Real name: {3}\n Identifier: {4}\n Channels:"
              " {5}\n Bot operator(s): {6}\n------------------------------".format(host, port, nick,
                                                            realname, ident, chans, botop))
        
    def prompt(self, field, default=None):
        '''Prompt a user for input, displaying a default value if one exists.'''
        if default:
            field += " [DEFAULT: {}]".format(default)
        field += ": "
        
        answer = ''
        while answer == '':
            answer = input(field)
            if default and answer == '':
                answer = default
        
        return answer
    
    def reconfigure(self):
        '''Overwrite the existing configuration file with a new one.'''
        try:
            os.remove(self.config_path)
        except:
            self.logger.error('Unable to remove existing configuration file.')
        else:
            self.config = configparser.ConfigParser()
            self.make_new()
    
    def setup_logging(self):
        '''Set up logging for the bot.'''
        if self.log_type != 'none':
            self.logger = logging.getLogger('GorillaBot')
            
            # Set logging level
            if self.quiet:
                self.logger.setLevel(logging.WARNING)
            else:
                self.logger.setLevel(logging.INFO)
            
            # Create the file logger
            if self.log_type != 'console':
                file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(threadName)s - "
                                                   "%(levelname)s : %(message)s")
                
                if not os.path.isdir(self.log_path):
                    os.mkdir(self.log_path)
                
                logname = (self.log_path + "/{0}.log").format(strftime("%H%M_%m%d%y"))
                
                # Files are saved in the logs sub-directory as HHMM_mmddyy.log
                # This log file rolls over every seven days.
                filehandler = logging.handlers.TimedRotatingFileHandler(logname,'d',7)
                filehandler.setFormatter(file_formatter)
                self.logger.addHandler(filehandler)
                self.logger.info("File logger created; saving logs to {}.".format(logname))
            
            # Create the console logger
            if self.log_type != "file":
                console_formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(levelname)s"
                                                      ": %(message)s", datefmt="%I:%M:%S %p")
                consolehandler = logging.StreamHandler()
                consolehandler.setFormatter(console_formatter)
                self.logger.addHandler(consolehandler)
                
                self.logger.info("Console logger created.")
                
    def verify(self):
        '''Verify that a configuration file is valid.'''
        for option in self.options:
            if not self.config.has_option("irc", option):
                print('Configuration file is invalid. Reconfiguring.')
                self.logger.info('Configuration file is invalid. Reconfiguring.')
                self.reconfigure()
        
        self.logger.info('Valid configuration file found.')
        
        if not self.default:
            # Allow reconfiguration even if the file is valid
            self.print_settings()
            reconfigure = ''
            while reconfigure != 'y' and reconfigure != 'n':
                reconfigure = input("Valid reconfiguration file found. Would you like to "
                                    "reconfigure? [Y/N] ")
                reconfigure.lower()
            if reconfigure == 'y':
                self.logger.debug('User has requested to reconfigure.')
                self.reconfigure()