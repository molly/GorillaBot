from plugins.util import command
import requests, re

SPOTIFY_URI_REGEX = r"(?<=spotify:)(?:track|album|artist):[a-zA-Z0-9]{22}"
ENDPOINT = "https://api.spotify.com/v1/%ss/%s"

@command()
def spotify(m):
    spotify_uris = re.finalall(SPOTIFY_URI_REGEX, m.body)
    for spotify_uri in spotify_uris:
        try:
            type, id = _parse_spotify_uri(spotify_uri)
            r = requests.get(ENDPOINT % (type, id))
            if r.status_code != 200:
                continue
            m.bot.private_message(m.location, r.json()["name"])
        except ValueError:
            pass

def _parse_spotify_uri(s):
    [type, id] = s.split(':')
    return type, id
