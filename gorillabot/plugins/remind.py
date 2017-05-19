# Copyright (c) 2013-2016 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from plugins.util import command
from dateparser import parse
import json
import re

dateparser_settings = {
    'TIMEZONE': 'US/Eastern',
    'PREFER_DAY_OF_MONTH': 'first',
    'PREFER_DATES_FROM': 'future'
}

@command()
def remind(m):
    """Remind someone of something at some time."""
    hostmask = m.bot.parse_hostmask(m.sender)
    line = m.line[1:]
    if line[0] == "me":
        line = line[1:]
    joined = " ".join(line)
    if not ":" in joined:
        time = joined
        reminder = None
    else:
        match = re.match(r'(.*)(?:\s?:\s?)(.*)', joined)
        time = match.group(1)
        reminder = match.group(2)
    parsed_time = parse(time, settings=dateparser_settings)
    if not parsed_time:
        m.bot.private_message(m.location, "I don't understand your reminder. Please see "
                                          "http://molly.github.io/GorillaBot for help with this command.")
        return
    parsed_time_str = str(parsed_time)
    new_reminder = {"hostmask": hostmask, "location": m.location, "reminder": "" if reminder is None else reminder}
    with open(m.bot.remind_path, 'r') as f:
        blob = json.load(f)
    if parsed_time_str in blob:
        # Handle the very improbable case where two reminders are set for the same exact time
        blob[parsed_time_str].append(new_reminder)
    else:
        blob[parsed_time_str] = [new_reminder]
    with open(m.bot.remind_path, "w") as f:
        json.dump(blob, f, indent=4)
