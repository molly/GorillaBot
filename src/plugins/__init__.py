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
 
__all__ = ["Command"]
 
import logging
 
class Command(object):
    '''Base command class. Provides the structure for each command; intended to be subclassed.'''
    
    # Name of the command
    name = None
    
    # Other commands that trigger this command
    aliases = []
    
    # Defines which command formats will trigger this command. "all" by default.
    triggers = ["all"]
    
    def __init__(self, bot, connection):
        '''Constructs the command object. Initializes logging.'''
        self.GorillaBot = bot
        self.GorillaConnection = connection
        self.logger = logging.getLogger("GorillaBot")
        
    def execute(self, line):
        '''Body of the command. Does nothing by default; must be subclassed.'''
        pass