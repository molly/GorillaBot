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

import argparse
from configure import Configurator
import logging
from logging import handlers
import os
from time import strftime


class Bot(object):
    """The core of the IRC bot. It maintains the IRC connection, and delegates other tasks."""

    def __init__(self):
        self.log_path = os.path.dirname(os.path.abspath(__file__)) + '/logs'
        self.logger = None
        self.settings = {}
        self.initialize()

    def initialize(self):
        """Initialize the bot. Parse command-line options, configure, and set up logging."""
        print('\n  ."`".'
              '\n / _=_ \\ \x1b[32m      __   __   __  . .   .     __   __   __  '
              '___\x1b[0m\n(,(oYo),) \x1b[32m    / _` /  \ |__) | |   |    |__| '
              '|__) /  \  |  \x1b[0m\n|   "   | \x1b[32m    \__| \__/ |  \ | |___'
              '|___ |  | |__) \__/  |  \x1b[0m \n \(\_/)/\n')

        # Parse arguments from the command line
        parser = argparse.ArgumentParser(description="This is the command-line utility for "
                                                     "setting up and running GorillaBot, "
                                                     "a simple IRC bot.")
        parser.add_argument("-d", "--default", action="store_true",
                            help="If a valid configuration file is found, this will proceed with "
                                 "the connection without asking for verification of settings.")
        parser.add_argument("-q", "--quiet", action="store_true",
                            help="Display log messages with level 'WARNING' or higher in the "
                                 "console.")
        args = parser.parse_args()
        configurator = Configurator(args.default)
        self.settings = configurator.get_configuration()
        self.setup_logging(args.quiet)

    def setup_logging(self, quiet):
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
        if quiet:
            consolehandler.setLevel(logging.WARNING)
        else:
            consolehandler.setLevel(logging.INFO)

        self.logger.addHandler(consolehandler)
        self.logger.info("Console logger created.")

if __name__ == "__main__":
    Bot()
