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
# OUT OF OR IN c.con WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

def _is_admin(c, channel, line):
    '''Verify that the sender of a command is a bot admin.'''
    sender = c.get_sender(line)
    if sender in c.con.admins:
        return True
    else:
        c.con.say("Ask a bot admin to perform this for you.", channel)
        return False

def addadmin(c, channel, command_type, line):
    '''Adds an administrator to the list of bot admins.'''
    if (_is_admin(c, channel, line)):
        regex = re.compile("!?addadmin\s(.*)",re.IGNORECASE)
        r = re.search(regex, line)
        if r:
            message = r.group(1).split()
            if len(message) == 1:
                c.con.admins.append(message)
                c.con.say("{} is now a bot admin.".format(message), channel)
            else:
                for user in message:
                    c.con.admins.append(user)
                users = ', '.join(message)
                c.con.say("{} are now bot admins.".format(users), channel)
            
def adminlist(c, channel, command_type, line):
    '''Prints a list of bot administrators.'''
    if len(c.con.admins) == 1:
        c.con.say("My bot admin is {}.".format(c.con.admins[0]), channel)
    else:
        adminlist = ', '.join(c.con.admins)
        c.con.say("My bot admins are: {}.".format(adminlist), channel)

def join(c, channel, command_type, line):
    '''Join a list of channels.'''
    if _is_admin(c, channel, line):
        regex = re.compile("!?join\s(.*)",re.IGNORECASE)
        r = re.search(regex, line)
        if r:
            chans = r.group(1).split()
            for chan in chans:
                if chan[0] == "#":
                    c.con.join(chan)
      
def emergencyshutoff(c, channel, command_type, line):
    '''Allows any user to kill the bot in case it malfunctions in some way.'''
    if command_type == "private":
        c.con.say("Shutting down.", channel)
        c.con.shut_down()

def part(c, channel, command_type, line):
    '''Part a list of channels.'''
    if _is_admin(c, channel, line):
        regex = re.compile("!?join\s(.*)",re.IGNORECASE)
        r = re.search(regex, line)
        if r:
            chans = r.group(1).split()
            for chan in chans:
                if chan[0] == "#":
                    c.con.part(chan)
        
def quit(c, channel, command_type, line):
    '''Quits IRC, shuts down the bot.'''
    if _is_admin(c, channel, line):
        c.con.shut_down()

def shutdown(c, channel, command_type, line):
    '''Alias for quit'''
    quit(c, channel, command_type, line)

def removeadmin(c, channel, command_type, line):
    '''Removes an admin from the list of bot admins.'''
    if _is_admin(c, channel, line):
        regex = re.compile("!?removeadmin\s(.*)",re.IGNORECASE)
        r = re.search(regex, line)
        if r:
            users = r.group(1).split()
            for user in users:
                if user in c.con.admins:
                    if len(c.con.admins) == 1:
                        c.con.say("You are the only bot administrator. Please add another"
                                  " admin or disconnect the bot before removing yourself.", channel)
                        return 0
                    c.con.admins.remove(user)
                    c.con.say("{} is no longer a bot admin.".format(user), channel)
                else:
                    c.con.say("{} is not on the list of bot admins.".format(user), channel)
