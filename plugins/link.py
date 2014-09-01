# Copyright (c) 2013-2014 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from plugins.util import command
import re
from urllib.request import Request, urlopen, URLError


@command()
def link(m, urls=None):
    if not urls:
        match = re.findall(r'(https?://\S+)', m.body)
        if match:
            urls = match
        else:
            m.bot.private_message(m.location, "Please provide a link.")
            return
    for url in urls:
        m.bot.logger.info("Retriving link for {}.".format(url))
        request = Request(url, headers=m.bot.header)
        try:
            html = urlopen(request)
        except URLError as e:
            m.bot.logger.info("{0}: {1}".format(url, e.reason))
        else:
            try:
                match = re.search(r'<title>(.+?)</title>', html.read().decode('utf-8'))
            except UnicodeDecodeError as e:
                m.bot.logger.info("{0}: {1}".format(url, e.reason))
            else:
                if match:
                    m.bot.private_message(m.location, "Link: " +
                                          re.sub('[\n\r\t]', ' ', match.group(1)))
