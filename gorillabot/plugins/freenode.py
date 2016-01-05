# Copyright (c) 2013-2016 Molly White
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

import logging
from getpass import getpass
import message
from queue import Empty


def identify(m):
    """Passes along Nickserv's password request and asks user to identify."""
    logger = logging.getLogger("GorillaBot")
    m.bot.response_lock.acquire()
    identified = False
    ignored_messages = []
    while not identified:
        password = getpass("Please enter your password to identify to NickServ: ")
        m.bot.private_message('NickServ', 'identify ' + password, True)
        while True:
            try:
                msg = m.bot.message_q.get(True, 120)
            except Empty:
                logger.error("No response from NickServ when trying to identify. Shutting down.")
                m.bot.shutdown.set()
                return
            if not isinstance(msg, message.Notice) or msg.sender != "NickServ!NickServ@services.":
                ignored_messages.append(msg)
                continue
            if 'Invalid' in msg.body:
                logger.info('Invalid password entered.')
                break
            elif 'You are now identified' in msg.body:
                logger.info('You have successfully identified.')
                identified = True
                m.bot.configuration["password"] = password
                m.bot.update_configuration(m.bot.configuration)
                break
            else:
                ignored_messages.append(msg)
    for msg in ignored_messages:
        m.bot.message_q.put(msg)
    m.bot.response_lock.release()
    m.bot.join()
