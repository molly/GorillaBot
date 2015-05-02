# Copyright (c) 2013-2015 Molly White
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

from plugins.util import command, get_url
from urllib.parse import quote
from html import unescape
from datetime import datetime
import json
import re


@command()
def link(m, urls=None, wikilinks=None):
    """Retrieve a description of the link, or provide a link to the English Wikipedia article if
    formatted as a wikilink."""

    #-     !link URL
    #-
    #- ```irc
    #- < GorillaWarfare> !link http://molly.github.io/GorillaBot/
    #- < GorillaBot> Link: GorillaBot
    #- < GorillaWarfare> !link https://www.youtube.com/watch?v=aSarf4-REgk
    #- < GorillaBot> Link: "Baby Gorilla Reunites With Mother" (01:43). Uploaded Mar 24,
    #-               2014. 164347 views. 513 likes, 32 dislikes.
    #- < GorillaWarfare> !link [[Gorilla]]
    #- < GorillaBot> https://en.wikipedia.org/wiki/Gorilla
    #- ```
    #-
    #- Provide information about the given link, or provide a link to the English Wikipedia article
    #- if formatted as a wikilink.
    #-
    #- In order to provide rich information about YouTube videos, you must provide a YouTube API
    #-  key when configuring the bot. You can get an API key by registering a project in the [
    #-  Google Developer Console](https://console.developers.google.com/). Without a key,
    #-  the normal linking will be used.
    #-
    #- #### Settings
    #- * `auto` - All links and wikilinks entered in the chat will be parsed, regardless of whether
    #-   they're prefaced with `!link`.

    if not (urls or wikilinks):
        urls = re.findall(r'(https?://\S+)', m.body)
        wikilinks = re.findall(r'\[{2}(.*?)\]{2}', m.body)
        if not (urls or wikilinks):
            m.bot.private_message(m.location, "Please provide a link.")
            return
    for url in urls:
        if "youtube.com" in url or "youtu.be" in url:
            message = youtube(m, url)
        elif "reddit.com" in url:
            message = reddit(m, url)
        else:
            message = generic(m, url)
        if message:
            m.bot.private_message(m.location, "Link: " + clean(message))
    for wikilink in wikilinks:
        safe = wikilink.replace(" ", "_")
        if safe[-1] == ")":
            safe = safe[:-1] + "%29"
        m.bot.private_message(m.location, "https://en.wikipedia.org/wiki/" + safe)


@command("relevantxkcd")
def xkcd(m):
    """Get an xkcd comic based on given arguments."""

    #-     !xkcd [number|query]
    #-
    #- ```irc
    #- < GorillaWarfare> !xkcd batman acne
    #- < GorillaBot> xkcd: Complexion: http://xkcd.com/700/
    #- < GorillaWarfare> !xkcd 700
    #- < GorillaBot> xkcd: Complexion: http://xkcd.com/700/
    #- < GorillaWarfare> !xkcd
    #- < GorillaBot> xkcd: Telescope Names: http://xkcd.com/1294/
    #- ```
    #-
    #- Without any arguments, this provides a random xkcd comic. When a number is supplied,
    #-  it tries to return the xkcd comic with that given number. When a query string is supplied,
    #-  it tries to return the xkcd comic that most closely matches that query.

    if len(m.line) == 1:
        url = "http://c.xkcd.com/random/comic/"
        html = get_url(m, url)
        message = xkcd_direct(html)
        if message is None:
            m.bot.logger.error("Couldn't get random xkcd comic.")
            message = "Sorry, I'm broken. Tell GorillaWarfare to fix me."
    elif len(m.line) == 2 and m.line[1].isdigit():
        url = "http://xkcd.com/{0}/".format(m.line[1])
        html = get_url(m, url)
        if html is None:
            m.bot.private_message(m.location, "There is no xkcd #{0}.".format(m.line[1]))
            return
        message = xkcd_direct(html, url)
        if message is None:
            m.bot.logger.error("Couldn't get xkcd comic #{0}.".format(m.line[1]))
            message = "Sorry, I'm broken. Tell GorillaWarfare to fix me."
    else:
        query = " ".join(m.line[1:])
        url = 'https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=site:xkcd.com%20{' \
              '0}'.format(quote(query))
        html = get_url(m, url)
        message = xkcd_google(html)
    m.bot.private_message(m.location, message)


def clean(title):
    """Clean the title so entities are unescaped and there's no weird spacing."""
    return unescape(re.sub('[\s]+', ' ', title))


def youtube(m, url):
    """Retrieve information about the YouTube video."""
    api_key = m.bot.configuration["youtube"]
    if api_key:
        match = re.search(r'youtu(?:be.com/watch\?v=|\.be/)(.+?)(?:\?|&|\Z)', url)
        if match:
            video_id = match.group(1)
            m.bot.logger.info("Retrieving information from the YouTube API for {}.".format(url))
            api_url = "https://www.googleapis.com/youtube/v3/videos?id={id}" \
                      "&key={key}&part=snippet,contentDetails,statistics"
            resp = get_url(m, api_url.format(id=video_id, key=api_key))
            if resp:
                # Load JSON
                blob = json.loads(resp)["items"][0]

                # Parse uploaded time
                raw_time = datetime.strptime(blob["snippet"]["publishedAt"],
                                             "%Y-%m-%dT%H:%M:%S.%fZ")
                pretty_time = raw_time.strftime("%b %d, %Y")

                # Parse video duration
                dur_match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(\d+)S',
                                     blob["contentDetails"]["duration"])
                hr, min, sec = dur_match.groups()
                if hr:
                    pretty_dur = ":".join([hr, "00" if min is None else min.zfill(2), sec.zfill(2)])
                else:
                    pretty_dur = ":".join(["00" if min is None else min.zfill(2), sec.zfill(2)])

                # Format and return message
                return "\"{title}\" ({duration}). Uploaded {date}. {views} views. {likes} likes, " \
                       "{dislikes} dislikes.".format(title=blob["snippet"]["title"],
                                                     duration=pretty_dur, date=pretty_time,
                                                     views=blob["statistics"]["viewCount"],
                                                     likes=blob["statistics"]["likeCount"],
                                                     dislikes=blob["statistics"]["dislikeCount"])
    # If there's no API key stored, or the URL is poorly formatted, fall back to generic linking
    return generic(m, url)


def reddit(m, url):
    """Retrieve information about the Reddit link."""

    # I'm sorry
    reddit_regex = re.compile(r'reddit\.com/(?:u(?:ser)?/(?P<user>.+?)(?:\Z|#|/)|r/(?P<sub>.+?)'
                              r'(?:/?\Z|/comments/(?P<id>.+?)(?:/?\Z|/(?P<title>.+?)'
                              r'(?:/?\Z|/(?P<cid>.+?)(?:/|#|\Z)))))')

    match = re.search(reddit_regex, url)
    if match:
        m.bot.logger.info("Retrieving information from the Reddit API for {}.".format(url))
        if match.group("user"):
            api_url = "http://www.reddit.com/user/{}/about.json"
            user = match.group("user")
            resp = get_url(m, api_url.format(user))
            blob = json.loads(resp)["data"]
            return "User {name}: {link_karma} link karma, {comment_karma} comment " \
                   "karma.".format(**blob)
        else:
            api_url = "http://www.reddit.com/api/info.json?id={}"
            sub, id, cid = match.group("sub"), match.group("id"), match.group("cid")
            if cid:
                resp = get_url(m, api_url.format("t1_" + cid))
                blob = json.loads(resp)["data"]["children"][0]["data"]
                parent_resp = get_url(m, api_url.format("t3_" + id))
                parent_blob = json.loads(parent_resp)["data"]["children"][0]["data"]
                parent_blob["nsfw"] = " \x0304[NSFW]\x03" if parent_blob["over_18"] else ""
                return "Comment by {user} on \"{title}\"{nsfw} in /r/{sub}. {up}↑.".format(
                    user=blob["author"], title=parent_blob["title"], nsfw=parent_blob["nsfw"],
                    sub=blob["subreddit"], up=blob["ups"])
            elif id:
                resp = get_url(m, api_url.format("t3_" + id))
                blob = json.loads(resp)["data"]["children"][0]["data"]
                blob["nsfw"] = "\x0304[NSFW]\x03" if blob["over_18"] else ""
                return "\"{title}\" in /r/{subreddit}. {ups}↑. {nsfw}".format(**blob)
            else:
                api_url = "http://www.reddit.com/r/{}/about.json"
                resp = get_url(m, api_url.format(sub))
                blob = json.loads(resp)["data"]
                blob["nsfw"] = "\x0304[NSFW]\x03" if blob["over18"] else ""
                return "/r/{display_name}. {title}. {subscribers} subscribers." \
                       " {nsfw}".format(**blob)
    return generic(m, url)


def generic(m, url):
    """Retrieve the title of the webpage."""
    m.bot.logger.info("Retrieving link for {}.".format(url))
    html = get_url(m, url, True)
    if html:
        title_regex = re.compile(r'<title>(.+?)</title>', re.DOTALL)
        match = re.search(title_regex, html)
        if match:
            return match.group(1)
        else:
            m.bot.logger.info("No title element found.")
            return None


def xkcd_direct(html, url=None):
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


def xkcd_google(html):
    """Try to pull out the first Google result for an xkcd comic."""
    blob = json.loads(html)
    results = blob['responseData']['results']
    if results == []:
        return "Could not retrieve xkcd using this query."
    else:
        return results[0]['titleNoFormatting'] + ': ' + results[0]['unescapedUrl']
