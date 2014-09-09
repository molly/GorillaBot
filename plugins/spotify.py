from plugins.util import command, get_url
import json
import re

SPOTIFY_URI_REGEX = r"(?<=spotify:)(?:track|album|artist):[a-zA-Z0-9]{22}"
ENDPOINT = "https://api.spotify.com/v1/{0}s/{1}"

@command()
def spotify(m):
    spotify_uris = re.findall(SPOTIFY_URI_REGEX, m.body)
    for spotify_uri in spotify_uris:
        try:
            type, id = _parse_spotify_uri(spotify_uri)
            req = get_url(m, ENDPOINT.format(type, id))
            if req:
                blob = json.loads(req)
                if type == "track" or type == "album":
                    m.bot.private_message(m.location,
                                          blob["artists"][0]["name"] + " - " + blob["name"])
                else:
                    m.bot.private_message(m.location, blob["name"])
        except ValueError:
            m.bot.logger.error("Invalid Spotify URI: " + spotify_uri)

def _parse_spotify_uri(s):
    [type, id] = s.split(':')
    return type, id
