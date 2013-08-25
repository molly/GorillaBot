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

import logging
from queue import Empty
from plugins.util import admin

def _identify(bot):
    logger = logging.getLogger("GorillaBot")
    bot.response_lock.acquire()
    bot.waiting_for_response = True
    identified = False
    while not identified:
        password = input("Please enter your password to identify to NickServ: ")
        bot.private_message('NickServ', 'identify ' + password, False)
        while True:
            try:
                response = bot.response_q.get(True, 120)
            except Empty:
                logger.error("No response from NickServ when trying to identify."
                             "Shutting down.")
                bot.shut_down()
            if 'NickServ' not in response[0]:
                continue
            if 'Invalid' in response[3]:
                logger.info('Invalid password entered.')
                break
            if 'identified' in response[6]:
                logger.info('You have successfully identified.')
                identified = True
                bot.waiting_for_response = False
                break
    bot.response_lock.release()