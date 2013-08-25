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

import logging, re
from queue import Empty
from plugins.util import admin, command

def _get_admin(bot, *users):
    bot.response_lock.acquire()
    logger = logging.getLogger('GorillaBot')
    if not users:
        users = bot.settings['botop']
    for user in users:
        bot.waiting_for_response = True
        bot.whois(user)
        while True:
            try:
                response = bot.response_q.get(True, 120)
            except Empty:
                logger.error("No whois response.")
            nick = None
            if response[1] == '311':
                nick = response[3]
                ident = response[4]
                host = response[5]
                break
            if response[1] == '401':
                break
        bot.waiting_for_response = False
        if nick:
            userinfo = [ident, host]
            if userinfo not in bot.admins.values():
                bot.admins[user] = userinfo
                logger.info('User {0} added to admin list (*!{1}@{2}).'
                            .format(nick, ident, host))
    bot.response_lock.release()

def _is_admin(bot, user):
    logger = logging.getLogger('GorillaBot')
    match = re.search('\:(?P<nick>.+?)!(?P<ident>.+?)@(?P<host>.+?)\Z', user)
    if match:
        sender_nick = match.group('nick')
        sender_ident = match.group('ident')
        sender_host = match.group('host')
    else:
        return False
    userinfo = [sender_ident, sender_host]
    if userinfo in bot.admins.values():
        return True
    else:
        if sender_nick in bot.settings['botop']:
            _get_admin(bot, sender_nick)
            return True
    return False

def _pong(bot, server):
    '''Respond to a ping from a server with a pong to that same server.'''
    bot.send('PONG {}'.format(server))