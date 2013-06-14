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
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERchannelTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN c.con WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
from urllib import parse

def link(c, channel, command_type, line):
    '''Return a link to the Wikipedia article; formatted as !link [[Article]]'''
    regex = re.compile("!?link\s([\[|\{]{2}(.*)[\]|\}]{2})",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        article_name = r.group(2)
        if article_name == None:
            c.con.say("Please format the command as !link [[article]] or !link {{template}}.", channel)
            return 0
        else:
            article_name = article_name.replace(" ", "_")
            url = parse.quote(article_name, safe="/#:")
            if "{{" in r.group(1):
                url = "http://en.wikipedia.org/wiki/Template:" + url
            else:
                url = "http://en.wikipedia.org/wiki/" + url
            c.con.say(url, channel)
    else:
        c.con.say("Please format the command as !link [[article]] or !link {{template}}.", channel)
        
def user(c, channel, command_type, line):
    '''Returns a link to the userpage; command formatted as !user Username'''
    regex = re.compile("!?user\s(.*)",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        username = r.group(1)
        username = username.strip("[]{}").replace(" ", "_")
        url = parse.quote(username, safe="/#:")
        url = "http://en.wikipedia.org/wiki/User:" + url
        c.con.say(url, channel)
    else:
        c.con.say("Please format this command as !usertalk username.", channel)
    
def usertalk(c, channel, command_type, line):
    '''Returns a link to the user talk page; command formatted as !usertalk Username'''
    regex = re.compile("!?usertalk\s(.*)",re.IGNORECASE)
    r = re.search(regex, line)
    if r:
        username = r.group(1)
        username = username.strip("[]{}").replace(" ", "_")
        url = parse.quote(username, safe="/#:")
        url = "http://en.wikipedia.org/wiki/User_talk:" + url
        c.con.say(url, channel)
    else:
        c.con.say("Please format this command as !usertalk username.", channel)