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
        except ValueError:
            m.bot.logger.error("Invalid Spotify URI: " + spotify_uri)
        else:
            req = get_url(m, ENDPOINT.format(type, id))
            if req:
                blob = json.loads(req)
                if type == "track" or type == "album":
                    m.bot.private_message(m.location, '"{0}" by {1} - {2}'
                                          .format(blob["name"], blob["artists"][0]["name"],
                                                  blob["external_urls"]["spotify"]))
                else:
                    m.bot.private_message(m.location, "{0} - {1}"
                                          .format(blob["name"], blob["external_urls"]["spotify"]))

def _parse_spotify_uri(s):
    [type, id] = s.split(':')
    return type, id
