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

import pickle, os, re

path = os.path.dirname(os.path.abspath(__file__))
print(path)

with open(path + '/langcodes.pickle', 'rb') as f:
    languages = pickle.load(f)
  
def lang(c, channel, command_type, line):
    match = re.search(r'!?lang\s(?P<code>[^\s]+)', line)
    if match:
        code = match.group('code').lower()
        if code in languages:
            c.con.say(code + ' is ' + languages[code] + '.', channel)
        else:
            c.con.say("No language code '" + code + "'.", channel)
    else:
        c.con.say('Please format this command !lang [code].', channel)
        
def reverse(c, channel, command_type, line):
    match = re.search(r'!?reverse\s(?P<code>.*)', line)
    if match:
        output = []
        lang = match.group('code').lower()
        for k,v in languages.items():
            if lang in v.lower() and ',' not in v:
                output.append(v + ' is ' + k)
        if len(output) > 0:
            output = ', '.join(output)
            c.con.say(output, channel)
        else:
            c.con.say("No language code for '" + lang + "'.", channel)
    else:
        c.con.say("Please format this command !reverse [language].")