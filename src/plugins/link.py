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

from urllib import parse

def link(connection, sender, chan, command_type, line):
    '''Return a link to the Wikipedia article; formatted as !link [[Article]]'''
    line.pop(0)
    if "[[" not in line[0] and "{{" not in line[0]:
        connection.say("Please format the command as !link [[article]] or !link {{template}}.",
                       chan)
        return 0
    end_index = ""
    for idx, word in enumerate(line):
        if "]]" in word or "}}" in word:
            end_index = idx + 1
    if type(end_index) != int:
        connection.say("Please format the command as !link [[article]] or !link {{template}}.", chan)
        return 0
    else:
        article_name = ' '.join(line[0:end_index])
        article_name = article_name.strip("[]{}").replace(" ", "_")
        url = parse.quote(article_name, safe="/#:")
        if "{{" in line[0]:
            url = "http://en.wikipedia.org/wiki/Template:" + url
        else:
            url = "http://en.wikipedia.org/wiki/" + url
        connection.say(url, chan)
        
def user(connection, sender, chan, command_type, line):
    '''Returns a link to the userpage; command formatted as !user Username'''
    line.pop(0)
    username = ' '.join(line[0:])
    username = username.strip("[]{}").replace(" ", "_")
    url = parse.quote(username, safe="/#:")
    url = "http://en.wikipedia.org/wiki/User:" + url
    connection.say(url, chan)
    
def usertalk(connection, sender, chan, command_type, line):
    '''Returns a link to the user talk page; command formatted as !usertalk Username'''
    line.pop(0)
    username = ' '.join(line[0:])
    username = username.strip("[]{}").replace(" ", "_")
    url = parse.quote(username, safe="/#:")
    url = "http://en.wikipedia.org/wiki/User_talk:" + url
    connection.say(url, chan)