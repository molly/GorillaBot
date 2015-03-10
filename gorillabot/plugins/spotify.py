from plugins.util import command, get_url
import json
import re

SPOTIFY_URI_REGEX = r"(?<=spotify)(?::|\.com/)(track|album|artist)(?::|/)([a-zA-Z0-9]{22})"
ENDPOINT = "https://api.spotify.com/v1/{0}s/{1}"


@command()
def spotify(m):
    """Retrieve information about a Spotify URI."""

    #-     !spotify URI
    #-
    #- ```irc
    #- < GorillaWarfare> !spotify spotify:track:6NmXV4o6bmp704aPGyTVVG
    #- < GorillaBot> "Bøn Fra Helvete (Live)" by Kaizers Orchestra
    #- ```
    #-
    #- Provide information about the Spotify URI. Accepts Spotify- and HTTP-style URIs.
    #-
    #- #### Settings
    #- * `auto` - All Spotify URIs in the chat will be parsed, regardless of whether they're
    #-  prefaced with `!spotify`.

    spotify_uris = re.findall(SPOTIFY_URI_REGEX, m.body)
    for spotify_uri in spotify_uris:
        media_type, identifier = spotify_uri
        req = get_url(m, ENDPOINT.format(media_type, identifier))
        if req:
            blob = json.loads(req)
            if media_type == "track" or media_type == "album":
                m.bot.private_message(m.location, '"{0}" by {1}'.format(blob["name"], blob["artists"][0]["name"]))
            else:
                m.bot.private_message(m.location, blob["name"])