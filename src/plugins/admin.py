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

def _is_admin(connection, sender, chan):
    '''Verify that the sender of a command is a bot admin.'''
    if sender in connection.admins:
        return True
    else:
        connection.say("Ask a bot admin to perform this for you.", chan, sender)
        return False

def addadmin(connection, sender, chan, command_type, line):
    '''Adds an administrator to the list of bot admins.'''
    if (_is_admin(connection, sender, chan) and command_type != "exclamation"):
        line.pop(0)
        # TODO: Verify that the user is online to make sure it was entered correctly
        for user in line:
            connection.admins.append(user)
            
def adminlist(connection, sender, chan, command_type, line):
    '''Prints a list of bot administrators.'''
    if len(connection.admins) == 1:
        connection.say("My bot admin is {}.".format(connection.admins[0]), chan, sender)
    else:
        adminlist = ', '.join(connection.admins)
        connection.say("My bot admins are: {}.".format(adminlist), chan, sender)

def join(connection, sender, chan, command_type, line):
    '''Join a list of channels.'''
    #TODO: Add validator for each chan to make sure it is formatted correctly
    if (_is_admin(connection, sender, chan) and command_type != "exclamation"):
        line.pop(0)
        connection.join(line)
        
def emergencyshutoff(connection, sender, chan, command_type, line):
    '''Allows any user to kill the bot in case it malfunctions in some way.'''
    if command_type == "private":
        connection.shut_down()

def part(connection, sender, chan, command_type, line):
    '''Part a list of channels.'''
    #TODO: Add validator for each chan to make sure it is formatted correctly
    if _is_admin(connection, sender, chan):
        line.pop(0)
        connection.part(line)
    
def removeadmin(connection, sender, chan, command_type, line):
    '''Removes an admin from the list of bot admins.'''
    if (_is_admin(connection, sender, chan) and command_type != "exclamation"):
        if len(connection.admins) == 1:
            connection.say("You are the only bot administrator. Please add another"
                           " admin or disconnect the bot before removing yourself.")
        line.pop(0)
        for user in line:
            # TODO: Tell a user if s/he has been removed from the admin list
            if user in connection.admins:
                connection.admins.remove(user)
                connection.say("{} is no longer a bot admin.".format(user), chan)
            else:
                connection.say("{} is not on the list of bot admins.".format(user), chan)
