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

import os
import configparser
import logging
from logging import handlers
from time import strftime

__all__ = ["Configure"]

class Configure(object):
    '''Creates, modifies, or opens a configuration file.'''
    
    def __init__(self, root, default, quiet):
        '''Constructs the configure object. Gets the path for the configuration file, assigns the
        logging type. Tries to load the configuration file.'''
        self._config = configparser.ConfigParser()
        self._config_path = os.path.dirname(os.path.abspath(__file__)) + "/config.cfg"
        self.log_path = os.path.dirname(os.path.abspath(__file__)) + "/logs"
        self._default = default
        self._quiet = quiet
        self._options = ("Host", "Port", "Nick", "Ident", "Realname", "Chans", "Botop", "Fullop")
        
        self._setup_logging("all")        
        self._load()
        
    def _prompt(self, question, default=None):
        '''Prompt a user for input. If there is a default set, display it.'''
        text = question
        if default:
            text += " [DEFAULT: {}]".format(default)
        text += ": "
        
        answer = ""
        while answer=="":
            answer = input(text)
            if default and answer=="":
                answer = default
        
        return answer
        
    def _load(self):
        '''Try to load a configuration file.'''
        file = self._config_path
        if os.path.isfile(file):
            try:
                self._config.read_file(open(self._config_path))
                self.logger.info("Opening {}.".format(self._config_path))
                self._verify()
            except IOError:
                self.logger.exception("Unable to open {}.".format(self._config_path))
        else:
            self.logger.info("No configuration file found. Creating file.")
            self._make_new(self._config)
    
    def _make_new(self, parser):
        '''Create a new configuration file.'''
        self._config = parser
        verify = ""
        while verify != "y":
            verify = ""
            print ("\n")
            host = self._prompt("Host", "irc.freenode.net")
            port = self._prompt("Port", 6667)
            nick = self._prompt("Nick", "GorillaBot")
            realname = self._prompt("Ident", "GorillaBot")
            ident = self._prompt("Realname", "GorillaBot")
            chans = self._prompt("Chans")
            botop = self._prompt("Bot operator(s)")
            print("------------------------------\n Host: {0}\n Port: {1}\n Nickname: "
              "{2}\n Real name: {3}\n Identifier: {4}\n Channels:"
              " {5}\n Bot operator(s): {6}\n------------------------------".format(host, port, nick,
                                                            realname, ident, chans, botop))
            while verify != "y" and verify != "n":
                verify = input ("Is this configuration correct? [Y/N]: ")
                verify = verify.lower()
                
        file = open(self._config_path, "w")
        parser.add_section("irc")
        parser.set("irc", "Host", host)
        parser.set("irc", "Port", str(port))
        parser.set("irc", "Nick", nick)
        parser.set("irc", "Realname", realname)
        parser.set("irc", "Ident", ident)
        parser.set("irc", "Chans", chans)
        parser.set("irc", "Botop", botop)
        parser.set("irc", "Fullop", '[]')
        parser.write(file)
        self.logger.info("Config file saved.")
        
    def _print_settings(self):
        '''Display the settings in a configuration file.'''
        host = self._config.get("irc", "Host")
        port = self._config.get("irc", "Port")
        nick = self._config.get("irc", "Nick")
        realname = self._config.get("irc", "Realname")
        ident = self._config.get("irc", "Ident")
        chans = self._config.get("irc", "Chans")
        botop = self._config.get("irc", "Botop")
        print("------------------------------\n Host: {0}\n Port: {1}\n Nickname: "
              "{2}\n Real name: {3}\n Identifier: {4}\n Channels:"
              " {5}\n Bot operator(s): {6}\n------------------------------".format(host, port, nick,
                                                            realname, ident, chans, botop))
        
    def _reconfigure(self):
        '''Create a new configuration file and overwrite the old one.'''
        try:
            os.remove(self._config_path)
        except:
            self.logger.exception("Unable to remove existing config file.")
        else:
            new_config = configparser.ConfigParser()
            self._make_new(new_config)            
        
    def _setup_logging(self, log_type="all"):
        '''Set up the logging for the bot.'''
        log_type = log_type.lower()
        inputs = ("all", "none", "console", "file")
        
        if log_type not in inputs:
            raise ValueError
        
        if log_type != "none":                
            self.logger = logging.getLogger("GorillaBot")
            if self._quiet:
                self.logger.setLevel(logging.WARNING)
            else:
                self.logger.setLevel(logging.INFO)
            
            #Create the file logger
            if log_type != "console":   
                file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s"
                                                   ": %(message)s")
                if not os.path.isdir(self.log_path):
                    os.mkdir(self.log_path)
                    
                logname = (self.log_path + "/{0}.log").format(strftime("%H%M_%m%d%y"))
                
                # Files are saved in the logs sub-directory as HHMM_mmddyy.log
                # If the session exceeds 6 hours, each file will have .# appended to
                # the end, up to five times. After these 30 hours, the logs will
                #begin to overwrite.
                filehandler = logging.handlers.TimedRotatingFileHandler(logname,'h',6,5,None,False,False)      
                filehandler.setFormatter(file_formatter)
                filehandler.setLevel(logging.DEBUG)
                self.logger.addHandler(filehandler)
                self.logger.info("File logger created; saving logs to {}.".format(logname))
            
            # Create the console logger    
            if log_type != "file":
                console_formatter = logging.Formatter("%(asctime)s - %(levelname)s"
                                                      ": %(message)s", datefmt="%I:%M:%S %p")
                consolehandler = logging.StreamHandler() 
                consolehandler.setFormatter(console_formatter)
                self.logger.addHandler(consolehandler)
                
                self.logger.info("Console logger created.")
                
    def _verify(self):
        '''Verify that a configuration file is valid.'''
        items = ("host", "port", "nick", "realname", "ident", "chans", "botop", "fullop")
        for option in items:
            exists = self._config.has_option("irc", option)
            if not exists:
                print("Configuration file is not valid. Reconfiguring.")
                self.logger.info("Configuration file is incorrectly formatted."
                                 " Reconfiguring.")
                self._reconfigure()
                break
            
        self.logger.info("Valid configuration file found.")
        reconfigure = ""
        if not self._default:
            while reconfigure != "y" and reconfigure !="n":
                self._print_settings()
                # Allow reconfiguration even if the config file is valid
                reconfigure = input("Valid configuration file found. Would you "
                                    "like to reconfigure? ")
                reconfigure = reconfigure.lower()
            if reconfigure == "y":
                self.logger.debug("User has requested to reconfigure.")
                self._reconfigure()
                
    def get_configuration(self):
        '''Return configuration as a dictionary.'''
        host = self._config.get("irc", "Host")
        port = int(self._config.get("irc", "Port"))
        nick = self._config.get("irc", "Nick")
        realname = self._config.get("irc", "Realname")
        ident = self._config.get("irc", "Ident")
        chans = self._config.get("irc", "Chans")
        botop = self._config.get("irc", "Botop")
        fullop = self._config.get("irc", "Fullop")
        chanlist = chans.split()
        oplist = botop.split()
        configuration = {"host":host, "port":port, "nick":nick,"realname":realname,
                         "ident":ident, "chans":chanlist, "botop":oplist, "fullop":fullop}
        return configuration
