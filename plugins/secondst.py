#!/usr/bin/env python
import requests
from BeautifulSoup import BeautifulSoup
from plugins.util import command

URL = 'http://www.2ndstcafe.com/'

@command("2ndst")
def secondst(m):
    r = requests.get(URL)
    if r.status_code != 200:
        m.bot.private_message(m.location, "Received non-200 status code: %d" % r.status_code)
        return
    soup = BeautifulSoup(r.text)
    items = map(lambda x: x.text, soup.findAll('li', {'class': None, 'id': None}))
    for item in items:
        if is_veggie(item):
            m.bot.private_message(m.location, "* %s" * % item)
        else:
            m.bot.private_message(m.location, item)

def is_veggie(s):
    return "vegan" in s.lower() or "vegetarian" in s.lower()
