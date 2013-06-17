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

def _is_admin(c, line, channel, exec_string):
    '''Verify that the sender of a command is a bot admin.'''
    c.con.full_admins = eval(c.con._bot._configuration._config.get("irc", "Fullop"))
    sender = c.get_sender(line)
    if sender in c.con.admins:
        c.con._whois_dest = ['isadmin', exec_string]
        c.con.whois(sender)
    else:
        c.con.say("Ask a bot admin to perform this for you.", channel)
        return False

def _is_admin_response(c, line, exec_string):
    nick = line[3]
    sender_id = line[4] + '@' + line[5]
    current_admins = c.con.full_admins
    for i in range(len(current_admins)):
        if nick == current_admins[i][0] and sender_id == current_admins[i][1]:
            exec(exec_string)
            c.con._whois_dest = None
            return
    c.con.say("Your cloak does not match the cloak on file.", nick)

def addadmin(c, channel, command_type, line):
    '''Adds an administrator to the list of bot admins.'''
    sender = c.get_sender(line)
    regex = re.compile("!?addadmin\s(.*)",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        c.con._whois_dest = ['adminlist', '']
        message = r.group(1).split()
        if len(message) == 1:
            c.con.admins.append(message[0])
            c.con.get_admin(message[0], sender)
            c.con.say("{} is now a bot admin.".format(message[0]), channel)
        else:
            for user in message:
                c.con.admins.append(user)
                c.con.get_admin(user, sender)
            users = ', '.join(message)
            c.con.say("{} are now bot admins.".format(users), channel)
    else:
        c.con.say("Please specify which user to add.", channel)
            
            
def adminlist(c, channel, command_type, line):
    '''Prints a list of bot administrators.'''
    print(c.con.full_admins)
    if len(c.con.admins) == 1:
        c.con.say("My bot admin is {}.".format(c.con.admins[0]), channel)
    else:
        adminlist = ', '.join(c.con.admins)
        c.con.say("My bot admins are: {}.".format(adminlist), channel)

def join(c, channel, command_type, line):
    '''Join a list of channels.'''
    regex = re.compile("!?join\s(.*)",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        chans = r.group(1).split()
        for chan in chans:
            c.con.join(chan)
    else:
        c.con.say("Please specify a channel to join (as !join #channel).", channel)
      
def emergencyshutoff(c, channel, command_type, line):
    '''Allows any user to kill the bot in case it malfunctions in some way.'''
    if command_type == "private":
        sender = c.get_sender(line)
        c.logger.error("Emergency shutdown requested by {}.".format(sender))
        c.con.say("Shutting down.", channel)
        c.con.shut_down()
    else:
        c.con.say("Please send this as a private message to shut me down.", channel)

def part(c, channel, command_type, line):
    '''Part a list of channels.'''
    regex = re.compile("!?part\s(.*)",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        chans = r.group(1).split()
        for chan in chans:
            c.con.part(chan)
    else:
        c.con.say("Please specify which channel to part (as !part #channel).", channel)
        
def quit(c, channel, command_type, line):
    '''Quits IRC, shuts down the bot.'''
    

def shutdown(c, channel, command_type, line):
    '''Alias for quit'''
    c.con.shut_down()

def removeadmin(c, channel, command_type, line):
    '''Removes an admin from the list of bot admins.'''
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
            else:
                c.con.say("{} is not on the list of bot admins.".format(user), channel)
                users.remove(user)
        if len(users) == 1:
            c.con.say("{} is no longer a bot admin.".format(users[0]), channel)
        else:
            users = ', '.join(users)
            c.con.say("{} are no longer bot admins.".format(users), channel)
    else:
        c.con.say("Please specify which admin to remove.", channel)
