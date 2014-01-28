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
# OUT OF OR IN c.con WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

def _is_admin(c, line, channel, exec_string):
    '''Verify that the sender of a command is a bot admin.'''
    c.con.full_admins = eval(c.con._bot._configuration._config.get("irc", "Fullop"))
    sender = c.get_sender(line)
    if sender in c.con.admins:
        c.con._whois_dest = ['isadmin', exec_string, sender]
        c.con.whois(sender)
    else:
        c.con._whois_dest = ['isadmin', exec_string, sender]
        c.con.names(channel)

def _is_admin_response(c, line, exec_string):
    '''Catch the whois response and execute the command if the user matches a bot admin.'''
    if line[1] == "311":
        nick = line[3]
        sender_id = line[4] + '@' + line[5]
        current_admins = c.con.full_admins
        for i in range(len(current_admins)):
            if nick == current_admins[i][0]:
                if sender_id == current_admins[i][1]:
                    c.con._whois_dest = None
                    exec(exec_string)
                    return
                elif current_admins[i][1] == '':
                    # Sender is in list of admins, but there's no cloak on file.
                    c.con.say("You are on the list of admins, but your cloak was not on file. Your cloak will be added; please resend the command.", nick)
                    c.con.get_admin(nick, None)
                    return
        c.con.say("Your cloak does not match the cloak on file.", nick)
    else:
        nick = c.con._whois_dest[2]
        if ('@' + nick) in line:
            #User is a channel operator
            c.con._whois_dest = None
            exec(exec_string)
            return
        else:
            c.con.say("Please ask a bot administrator or channel operator to perform this command for you.", nick)

def _nick_change(c, line):
    c.con.full_admins = eval(c.con._bot._configuration._config.get("irc", "Fullop"))
    original = re.search(r'\:(?P<nick>.*?)\!', line[0])
    if original:
        original = original.group('nick')
        nick = line[2][1:]
        for i in range(len(c.con.admins)):
            if original == c.con.admins[i]:
                c.con.admins[i] = nick
        for i in range(len(c.con.full_admins)):
            if original == c.con.full_admins[i][0]:
                c.con.full_admins[i][0] = nick
        config = c._bot._configuration._config
        file = c._bot._configuration._config_path
        config.set("irc", "Botop", " ".join(c.con.admins))
        config.set("irc", "Fullop", repr(c.con.full_admins))
        with open(file, 'w') as configfile:
            config.write(configfile)

def addadmin(c, channel, command_type, line):
    '''Adds an administrator to the list of bot admins.'''
    sender = c.get_sender(line)
    regex = re.compile("!?addadmin\s(?P<nick>[^\s]+)",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        nick = r.group('nick')
        if nick not in c.con.admins:
            c.con.admins.append(nick)
            config = c._bot._configuration._config
            file = c._bot._configuration._config_path
            config.set("irc", "Botop", " ".join(c.con.admins))
            with open(file, 'w') as configfile:
                config.write(configfile)
            c.con._whois_dest = ['adminlist', '']
            c.con.get_admin(nick, sender)
            c.con.say("{} is now a bot admin.".format(nick), channel)
        else:
            c.con.say("{} is already a bot admin.".format(nick), channel)
    else:
        c.con.say("Please format the command !addadmin [nick]", channel)

def adminlist(c, channel, command_type, line):
    '''Prints a list of bot administrators.'''
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
    c.con.shut_down()

def shutdown(c, channel, command_type, line):
    '''Alias for quit'''
    c.con.shut_down()

def removeadmin(c, channel, command_type, line):
    '''Removes an admin from the list of bot admins.'''
    c.con.full_admins = eval(c.con._bot._configuration._config.get("irc", "Fullop"))
    config = c._bot._configuration._config
    file = c._bot._configuration._config_path
    regex = re.compile("!?removeadmin\s(?P<nick>[^\s]+)",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        nick = r.group('nick')
        if nick in c.con.admins:
            if len(c.con.admins) == 1:
                c.con.say("You are the only bot administrator. Please add another"
                          " admin or disconnect the bot before removing yourself.", channel)
                return
            c.con.admins.remove(nick)
            for i in range(len(c.con.full_admins)):
                if c.con.full_admins[i][0] == nick:
                    c.con.full_admins.pop(i)
                    config.set("irc", "Botop", " ".join(c.con.admins))
                    config.set("irc", "Fullop", repr(c.con.full_admins))
                    with open(file, 'w') as configfile:
                        config.write(configfile)
                    break
            c.con.say("{} is no longer a bot admin.".format(nick), channel)
        else:
            c.con.say("{} is not on the list of bot admins.".format(nick), channel)
    else:
        c.con.say("Please format this command !removeadmin [nick].", channel)
