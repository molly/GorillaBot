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
import sys
from time import strftime

__all__ = ["Configure"]

class Configure(object):
    '''Creates, modifies, or opens a configuration file.'''
    
    def __init__(self, root, default):
        self._config = configparser.ConfigParser()
        self._config_path = os.path.join(root, "config.cfg")
        self._default = default
        self.logger = logging.getLogger("GorillaBot")
        
        self._options = ("Host", "Port", "Nick", "Ident", "Realname", "Chans")
        
        self.setup_logging("console")        
        self.load()
        
    def _prompt(self, question, default=None):
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
        
    def load(self):
        file = self._config_path
        if os.path.isfile(file):
            try:
                self._config.read_file(open(self._config_path))
                self.logger.debug("Opening {}.".format(self._config_path))
                self.verify()
            except IOError:
                self.logger.exception("Unable to open {}.".format(self._config_path))
        else:
            self.logger.debug("No configuration file found. Creating file.")
            self.make_new(self._config)
    
    def make_new(self, parser):
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
            print("\n------------------------------\n Host: {0}\n Port: {1}\n Nickname: "
              "{2}\n Real name: {3}\n Identifier: {4}\n Channels:"
              " {5}\n------------------------------".format(host, port, nick,
                                                            realname, ident, chans))
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
        parser.write(file)
        
    def print_settings(self):
        host = self._config.get("irc", "Host")
        port = self._config.get("irc", "Port")
        nick = self._config.get("irc", "Nick")
        realname = self._config.get("irc", "Realname")
        ident = self._config.get("irc", "Ident")
        chans = self._config.get("irc", "Chans")
        print("\n------------------------------\n Host: {0}\n Port: {1}\n Nickname: "
              "{2}\n Real name: {3}\n Identifier: {4}\n Channels:"
              " {5}\n------------------------------".format(host, port, nick,
                                                            realname, ident, chans))
        
    def reconfigure(self):
        try:
            os.remove(self._config_path)
        except:
            self.logger.exception("Unable to remove existing config file.")
        else:
            new_config = configparser.ConfigParser()
            self.make_new(new_config)            
        
    def setup_logging(self, log_type="all"):
        log_type = log_type.lower()
        inputs = ("all", "none", "console", "file")
        
        if log_type not in inputs:
            raise ValueError
        
        if log_type != "none":                
            self.logger = logging.getLogger("GorillaBot")
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s"
                                          ": %(message)s")
            
            if log_type != "console":   
                if not os.path.isdir(os.curdir + "/logs"):
                    os.mkdir(os.curdir + "/logs")
                    
                logname = "logs/{0}.log".format(strftime("%H%M_%m%d%y"))
                # Files are saved in the logs sub-directory as HHMM_mmddyy.log
                # If the session exceeds 6 hours, each file will have .# appended to
                # the end, up to five times. After these 30 hours, the logs will
                #begin to overwrite.
                filehandler = logging.handlers.TimedRotatingFileHandler(logname,'h',
                                                                        6,5,None,
                                                                        False,False)      
                filehandler.setFormatter(formatter)
                self.logger.addHandler(filehandler)
                
            if log_type != "file":
                consolehandler = logging.StreamHandler() 
                consolehandler.setFormatter(formatter)
                self.logger.addHandler(consolehandler)
                
                self.logger.info("Console logger created.")
                
            if log_type != "console":
                self.logger.info("File logger created; "
                                 "saving logs to {}.".format(logname))
                
    def verify(self):
        items = ("host", "port", "nick", "realname", "ident", "chans")
        for option in items:
            exists = self._config.has_option("irc", option)
            if not exists:
                print("Configuration file is not valid. Reconfiguring.")
                self.logger.info("Configuration file is incorrectly formatted."
                                 " Reconfiguring.")
                self.reconfigure()
                break
        self.logger.debug("Valid configuration file found.")
        reconfigure = ""
        if not self._default:
            while reconfigure != "y" and reconfigure !="n":
                self.print_settings()
                reconfigure = input("Valid configuration file found. Would you "
                                    "like to reconfigure? ")
                reconfigure = reconfigure.lower()
            if reconfigure == "y":
                self.logger.debug("User has requested to reconfigure.")
                self.reconfigure()
