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

from plugins.util import command, get_url
from bs4 import BeautifulSoup


@command("b", "qdb")
def bash(m):
    """Return a quote from bash.org."""

    #-     !bash [number]
    #-
    #- ```irc
    #- < GorillaWarfare> !bash
    #- < GorillaBot> --- #64 (859) http://bash.org?64 ----------------------------------------------
    #- < GorillaBot> <Ash> Win2k! ^_^
    #- < GorillaBot> *** Ash Quit (Read error: 73 (Connection reset by peer))
    #- < GorillaBot> -------------------------------------------------------------------------------
    #- < GorillaWarfare> !bash 400459
    #- < GorillaBot> --- #400459 (13378) http://bash.org?400459 ------------------------------------
    #- < GorillaBot> <Sonium> someone speak python here?
    #- < GorillaBot> <lucky> HHHHHSSSSSHSSS
    #- < GorillaBot> <lucky> SSSSS
    #- < GorillaBot> <Sonium> the programming language
    #- < GorillaBot> -------------------------------------------------------------------------------
    #-
    #- Post a quote from bash.org. If given a quote number, it will try to post it. Otherwise it
    #- will post a random quote. If the quote is too long, it will direct the user to the URL.
    #- Please note that there is no filtering here, so some of the quotes may be inappropriate.

    if len(m.line) > 1 and m.line[1].isnumeric():
        bash_specific(m, m.line[1])
    else:
        bash_rand(m)


def bash_rand(m):
    """Get a random quote from bash.org"""
    resp = get_url(m, "http://bash.org?random")
    soup = BeautifulSoup(resp)
    raw = soup.find(class_="qt")
    if raw:
        meta = soup.find(class_="quote")
        while True:
            if not raw:
                bash_rand(m)
                return
            lines = raw.get_text().splitlines()
            if len(lines) <= 5:
                break
            raw = raw.find_next(class_="qt")
            meta = soup.find_next(class_="quote")
        format_quote(m, lines, meta)
    else:
        m.bot.private_message(m.location, "Could not find bash quote.")


def bash_specific(m, number):
    """Get a specific quote from bash.org."""
    resp = get_url(m, "http://bash.org?" + number)
    soup = BeautifulSoup(resp)
    raw = soup.find(class_="qt")
    if raw:
        meta = soup.find(class_="quote")
        lines = raw.get_text().splitlines()
        if len(lines) > 5 and not m.is_pm:
            m.bot.private_message(m.location, "This quote is too long to post publicly, "
                                              "but you can view it at http://bash.org?"
                                              "{}.".format(number))
        else:
            format_quote(m, lines, meta, number)
    else:
        m.bot.private_message(m.location, "Could not find bash quote.")


def format_quote(m, raw, meta, number=None):
    """Format the quote with some metadata."""
    try:
        score = meta.font.string
        score_str = "\x0304{}\x03".format(score) if "-" in score else "\x0303{}\x03".format(score)
        url = "http://bash.org?" + (number if number else meta.b.string.strip("#"))
        meta_str = "--- {} ({}) {} ".format(meta.b.string, score_str, url)
    except AttributeError as e:
        if number:
            m.bot.private_message(m.location, "Could not find bash quote.")
        else:
            bash_rand(m)
    else:
        m.bot.private_message(m.location, meta_str.ljust(83, '-'))
        for line in raw:
            m.bot.private_message(m.location, line)
        m.bot.private_message(m.location, "-" * 80)
