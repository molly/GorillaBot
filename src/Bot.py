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

from time import strftime
import os
from Connect import Connection
import logging
from logging import handlers

class Bot(object):
    def __init__(self):
        self.setup_logging("console")
        
    def setup_logging(self, log_type="all"):
        log_type = log_type.lower()
        inputs = ("all", "none", "console", "file")
        
        if log_type not in inputs:
            raise ValueError
        
        if log_type != "none":                
            self.logger = logging.getLogger("GorillaBot")
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s "
                                          "- %(message)s")
            
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
                filehandler.setLevel(logging.DEBUG)        
                filehandler.setFormatter(formatter)
                self.logger.addHandler(filehandler)
                
            if log_type != "file":
                consolehandler = logging.StreamHandler()
                consolehandler.setLevel(logging.DEBUG)    
                consolehandler.setFormatter(formatter)
                self.logger.addHandler(consolehandler)
                
                self.logger.info("Console logger created.")
                
            if log_type != "console":
                self.logger.info("File logger created; "
                                 "saving logs to {}.".format(logname))
