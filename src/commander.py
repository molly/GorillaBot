# Copyright (c) 2013-2014 Molly White
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
from bot import Bot

def main():
    print('\n  ."`".'
          '\n / _=_ \\ \x1b[32m      __   __   __  . .    .     __   __   __  ___\x1b[0m'
          '\n(,(oYo),) \x1b[32m    / _` /  \ |__) | |    |    |__| |__) /  \  |  \x1b[0m'
          '\n|   "   | \x1b[32m    \__| \__/ |  \ | |___ |___ |  | |__) \__/  |  \x1b[0m'
          '\n \(\_/)/\n')

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

    # Create instance of bot, create connection
    Bot(args.path, args.default, args.quiet)

if __name__ == "__main__":
    main()
