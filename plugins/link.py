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
from html.parser import HTMLParser
from urllib.request import Request, urlopen, URLError
from urllib.parse import quote
import json
import re


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
        m.bot.logger.info("Retrieving link for {}.".format(url))
        html = _get_url(m, url)
        if html:
            try:
                match = re.search(r'<title>(.+?)</title>', html)
            except UnicodeDecodeError as e:
                m.bot.logger.info("{0}: {1}".format(url, e.reason))
            else:
                if match:
                    h = HTMLParser()
                    m.bot.private_message(m.location, "Link: " +
                                          h.unescape(re.sub('[\n\r\t]', ' ', match.group(1))))

@command("relevantxkcd")
def xkcd(m):
    """Get an xkcd comic based on given arguments."""
    if len(m.line) == 1:
        url = "http://c.xkcd.com/random/comic/"
        html = _get_url(m, url)
        message = _xkcd_direct(html)
        if message is None:
            m.bot.logger.error("Couldn't get random xkcd comic.")
            message = "Sorry, I'm broken. Tell GorillaWarfare to fix me."
    elif len(m.line) == 2 and m.line[1].isdigit():
        url = "http://xkcd.com/{0}/".format(m.line[1])
        html = _get_url(m, url)
        if html is None:
            m.bot.private_message(m.location, "There is no xkcd #{0}.".format(m.line[1]))
            return
        message = _xkcd_direct(html, url)
        if message is None:
            m.bot.logger.error("Couldn't get xkcd comic #{0}.".format(m.line[1]))
            message = "Sorry, I'm broken. Tell GorillaWarfare to fix me."
    else:
        query = " ".join(m.line[1:])
        url = 'https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=site:xkcd.com%20{0}'\
              .format(quote(query))
        html = _get_url(m, url)
        message = _xkcd_google(html)
    m.bot.private_message(m.location, message)

def _get_url(m, url):
    """Request a given URL, handling any errors."""
    request = Request(url, headers=m.bot.header)
    try:
        html = urlopen(request)
    except URLError as e:
        m.bot.logger.info("{0}: {1}".format(url, e.reason))
        return None
    else:
        return html.read().decode('utf-8')

def _xkcd_direct(html, url=None):
    """Try to return a title and link for a direct link to an xkcd comic."""
    if not html:
        return None
    if not url:
        url_match = re.search(r'Permanent link to this comic: ([^\s<>]+)', html)
        if url_match:
            url = url_match.group(1)
        else:
            return None
    match = re.search(r'<title>(.+?)</title>', html)
    if match:
        return match.group(1) + ": " + url
    else:
        return None

def _xkcd_google(html):
    """Try to pull out the first Google result for an xkcd comic."""
    blob = json.loads(html)
    results = blob['responseData']['results']
    if results == []:
        return "Could not retrieve xkcd using this query."
    else:
        return results[0]['titleNoFormatting'] + ': ' + results[0]['unescapedUrl']