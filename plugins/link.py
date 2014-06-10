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

from bs4 import BeautifulSoup
from plugins.util import command
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen, URLError


@command()
def link(m, urls=None):
    if urls is None:
        match = re.search(r'(https?://\S+)', m.body)
        if match:
            urls = match.groups()
        else:
            m.bot.private_message(m.location, "Please provide a link.")
            return
    for url in urls:
        m.bot.logger.info("Retrieving link for " + url)
        request = Request(url, headers=m.bot.header)
        try:
            html = urlopen(request)
        except URLError as e:
            # Don't try to do anything fancy, just ignore the URL
            m.bot.logger.info(e.reason)
            pass
        else:
            parsed = urlparse(url)
            soup = BeautifulSoup(html)
            if parsed.netloc == "www.twitch.tv":
                meta = (soup.find(property="og:title"), soup.find(property="og:description"))
                meta = [x["content"] for x in meta if x]
                message = m.location, " - ".join(meta)
            elif parsed.netloc == "www.youtube.com" or parsed.netloc == "youtu.be":
                title = soup.find(itemprop="name")
                duration = soup.find(itemprop="duration")
                if duration:
                    duration = re.match(r'PT(?P<min>\d+)M(?P<sec>\d+)S', duration["content"])
                    if duration.group("min") == "00":
                        time = duration.group("sec") + "s"
                    else:
                        time = duration.group("min") + "m" + duration.group("sec") + "s"
                message = "YouTube - " + title["content"]
                if duration:
                    message += " (" + time + ")"
            elif parsed.netloc == "www.imgur.com":
                message = "Imgur - " + soup.title.string.strip()
            elif parsed.netloc == "www.reddit.com":
                if "comments" in url:
                    user = None
                    if (url[-1] != "/" and parsed.path.count("/") == 6) or \
                            (url[-1] == "!" and parsed.path.count("/") == 7):
                        # Comment link
                        title = soup.find("p", class_="title")
                        if title:
                            c_id = url.rsplit("/", maxsplit=1)[1]
                            comment = soup.find("div", class_ = "id-t1_" + c_id)\
                                .find("div", class_="entry")
                            if comment:
                                user = comment.find("a", class_="author").string
                                title = "Comment by " + user + " on \"" + title.a.string + "\""
                            else:
                                title = "Comment on \"" + title.a.string + "\""
                    else:
                        title = soup.find("p", class_="title")
                        if title:
                            title = "\"" + title.a.string + "\""
                    sub = soup.find("h1", class_="redditname")
                    if sub:
                        sub = "r/" + sub.a.string
                    linkinfo = soup.find("div", "linkinfo")
                    votes = None
                    if linkinfo and not user:
                        up = linkinfo.find("span", "upvotes").find("span", class_="number")
                        down = linkinfo.find("span", "downvotes").find("span", class_="number")
                        if up and down:
                            votes = "(" + up.string + "↑ " + down.string + "↓)"
                    msg = [x for x in (title, votes, sub) if x]
                    message = " - ".join(msg)
                elif "/r/" in url:
                    sub = soup.find("h1", class_="redditname")
                    message = "Reddit - r/" + sub.a.string
                else:
                    message = soup.title.string
            else:
                message = soup.title.string
            m.bot.private_message(m.location, "Link: " + message)
