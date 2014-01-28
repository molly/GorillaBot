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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY Kself.ind, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN c.con WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

class Stalker(object):
    def __init__(self):
        self.stalk_dict = dict()
        self.notify_dict = dict()
        self.current_nick = '' # Who is the notify set on?
        self.current_sender = '' # Who set the notify?
        self.channel = '' # From where was the notify set?
        self.codes = []
        self.con = None
        self.notify_status = False # Are we setting up an initial notify?

    def _recv_numcode(self, con, nick):
        '''Interpret numcodes from the whois response.'''
        self.con = con
        if self.notify_status:
            # Determining initial connection status
            if '401' in self.codes:
                # User is offline
                self.con.say('You will be notified when {} comes online.'.format(self.current_nick), self.channel)
                self.notify_dict[self.current_nick][0] = 'offline'
            elif '301' in self.codes:
                # User is away
                self.con.say('You will be notified when {} returns from away.'.format(self.current_nick), self.channel)
                self.notify_dict[self.current_nick][0] = 'away'
            else:
                self.con.say('{} is already online.'.format(self.current_nick), self.channel)
                if len(self.notify_dict[self.current_nick][1]) == 1:
                    del self.notify_dict[self.current_nick]
                else:
                    self.notify_dict[self.current_nick][1].remove(self.current_sender)
                    self._notify_watchers(self.current_nick)
        else:
            # Updating
            if '401' in self.codes:
                if self.notify_dict[nick][0] == 'away':
                    for user in self.notify_dict[nick][1]:
                        self.con.private_message(user, '{0} has gone offline. You will be notified when {0} returns'.format(nick))
                    self.notify_dict[nick][0] = 'offline'
            elif '301' in self.codes:
                if self.notify_dict[nick][0] != 'away':
                    for user in self.notify_dict[nick][1]:
                        self.con.private_message(user, '{} has returned, but is marked as away.'.format(nick))
                    self.notify_dict[nick][0] = 'away'
            else:
                if nick in self.notify_dict:
                    for user in self.notify_dict[nick][1]:
                        self.con.private_message(user, '{} has returned.'.format(nick))
                    del self.notify_dict[nick]
        self._clear()
        self.con._whois_dest = None
        self.notify_status = False

    def _clear(self):
        '''Clear state information'''
        self.current_nick = '' # Who is the notify set on?
        self.current_sender = '' # Who set the notify?
        self.channel = '' # From where was the notify set?
        self.status = '' # Away, online, offline
        self.codes = []
        self.con = None

    def _nick_change(self, line):
        '''Called when a user changes nick to update the notify dict.'''
        match = re.search(r':(?P<nick>.*?)!', line[0])
        if not match:
            return
        old_nick = match.group('nick')
        new_nick = line[2][1:]
        if old_nick in self.notify_dict:
            self.notify_dict[new_nick] = self.notify_dict[old_nick]
            del self.notify_dict[old_nick]
        for nick in self.notify_dict.keys():
            for num in range(len(self.notify_dict[nick][1])):
                if self.notify_dict[nick][1][num] == old_nick:
                    self.notify_dict[nick][1][num] = new_nick

    def _update(self, bot):
        '''Called repeatedly to check if anyone has come online/back.'''
        self.con = bot.GorillaConnection
        for nick in self.notify_dict.keys():
            self.con.whois(nick)

    def notify(self, c, channel, command_type, line):
        '''Command to notify a user if another user comes online or back from away.'''
        self.con = c.con
        self.channel=channel
        self._clear() # Once more for good measure
        user = re.search(r'notify\s(?P<nick>[^\s]+)(?P<extra>.+)?', line)
        if user:
            if user.group('extra'):
                self.con.say("You have used too many parameters. Please only set notification "
                          "on one nick at a time.", channel)
                return
            elif user.group('nick'):
                self.current_nick = user.group('nick')
        else:
            self.con.say("Please specify a nick.", channel)
            return
        self.current_sender = c.get_sender(line)
        if self.current_nick not in self.notify_dict:
            self.notify_dict[self.current_nick] = ['', [self.current_sender]]
            self.con._whois_dest = ['notify', '']
            self.notify_status = True
        else:
            if self.current_sender in self.notify_dict[self.current_nick][1]:
                self.con.say("{} is already in your notify list. Did you mean to denotify?".format(self.current_nick), channel)
                return
            else:
                self.notify_dict[self.current_nick][1].append(self.current_sender)
                self.con._whois_dest = ['notify', '']
                self.notify_status = True
        self.con.whois(self.current_nick)
