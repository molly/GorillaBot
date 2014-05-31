# Copyright (c) 2013-2014 Molly White
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

from plugins.util import admin

@admin()
def join(m):
    """Join a channel."""
    if len(m.line) == 1:
        m.bot.private_message(m.location, "Please specify a channel to join.")
    else:
        if m.line[1][0] != "#":
            m.bot.join(["#" + m.line[1]])
            m.bot.logger.info("Joining #" + m.line[1])
        else:
            m.bot.join(m.line[1])
            m.bot.logger.info("Joining " + m.line[1])

@admin("leave")
def part(m):
    """Part from the specified channel."""
    part_msg = ""
    if len(m.line) == 1:
        m.bot.send("PART " + m.location + " " + part_msg)
        m.bot.logger.info("Parting from #" + m.location)
        return
    channel = ""
    if len(m.line) > 2:
        part_msg = " ".join(m.line[2:])
    if m.line[1][0] != "#":
        channel = "#" + m.line[1]
    else:
        channel = m.line[1]
    if channel in m.bot.channels:
        m.bot.send("PART " + channel + " :" + part_msg)
        m.bot.logger.info("Parting from " + channel + ".")
    else:
        m.bot.private_message(m.location, "Not joined to " + channel + ".")
