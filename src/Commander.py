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

import argparse
from os import path
from Bot import Bot
import logging
import sys

def main():
    print ("\nStarting GorillaBot.")
    desc = "This is the command-line utility for setting up and running GorillaBot, "
    "a simple IRC bot."
    
    # Parse arguments from the command line
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("path", nargs="?", default=path.curdir, help="Path to the"
                        " bot configuration file. Assumes current directory if no"
                        " path is specified.")
    parser.add_argument("-d", "--default", action="store_true", help="If a valid"
                        " configuration file is found, this will proceed with the"
                        " connection without asking for verification of settings.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Only log "
                        "messages with level 'WARNING' or higher.")
    args = parser.parse_args()
    
    # Initialize logger
    logger = logging.getLogger("GorillaBot")
    
    # Create instance of bot
    GorillaBot = Bot(args.path, args.default, args.quiet)
    
    # Connect to the IRC server
    time_to_connect = ""
    while time_to_connect != "y":
        time_to_connect = input("Connect to the IRC server now? [Y/N/exit] ")
        time_to_connect = time_to_connect.lower()
        if time_to_connect == "exit" or time_to_connect == "e":
            logger.info("User requested to exit the bot.")
            sys.exit()
    logger.info("User has asked to connect to the IRC server.")
    nickserv = ""
    while nickserv != "y" and nickserv != "n":
        nickserv = input("Identify to NickServ? [Y/N] ")
        nickserv = nickserv.lower()
    if nickserv == "y":
        nickserv = True
    else:
        nickserv = False
    GorillaBot.begin_connection(nickserv)
    

if __name__ == "__main__":
    main()
