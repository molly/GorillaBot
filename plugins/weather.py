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

import json
from plugins.util import command, get_url
from urllib.parse import quote


@command()
def weather(m):
    """Get the weather for a specified location."""

    #-     !weather location
    #-
    #- ```irc
    #- < GorillaWarfare> !weather boston
    #- < GorillaBot> Weather in Boston, MA, USA: Mostly cloudy until tomorrow morning.
    #-               59˚F (15.0˚C). Humidity: 92%.
    #- ```
    #-
    #- Provide weather information for the given location.
    #-
    #- In order to provide weather information, you must provide a Forecast.io API key when
    #-  configuring the bot. You can get an API key by registering an email address at
    #-  http://developer.forecast.io/.

    api_key = m.bot.get_config('forecast')
    if api_key:
        if len(m.line) <= 1:
            m.bot.private_message(m.location, "Please format this command as !weather ["
                                              "args] location")
        else:
            if m.line[1] in ["--now", "-now", "-n"]:
                loc = get_location(m, args=True)
                blob = get_weather(m, loc, api_key)
                msg = format_weather(blob, loc, "currently")
            else:
                loc = get_location(m)
                blob = get_weather(m, loc, api_key)
                msg = format_weather(blob, loc, "hourly")
            m.bot.private_message(m.location, msg)
    else:
        m.bot.logger.info("No Forecast.io API key recorded.")


def get_location(m, args=False):
    """Get the latitude, longitude, and well-formatted name of the given location."""
    google_api = "http://maps.googleapis.com/maps/api/geocode/json?address={}"
    loc = {}
    if args:
        loc["name"] = " ".join(m.line[2:])
        resp = get_url(m, google_api.format("+".join(m.line[2:])))
    else:
        loc["name"] = " ".join(m.line[1:])
        resp = get_url(m, google_api.format("+".join(m.line[1:])))
    blob = json.loads(resp)
    if not blob["results"]:
        m.bot.private_message(m.location, "Could not find weather information for {}."
                              .format(" ".join(m.line[1:])))
    else:
        loc["lat"] = blob['results'][0]['geometry']['location']['lat']
        loc["long"] = blob['results'][0]['geometry']['location']['lng']
        loc["addr"] = blob['results'][0]['formatted_address']
        return loc


def get_weather(m, loc, api_key):
    """Make the API call to get the weather."""
    if loc:
        m.bot.logger.info("Finding weather for {}.".format(loc["name"]))
        forecast_api = "https://api.forecast.io/forecast/{0}/{1},{2}?exclude=flags"
        resp = get_url(m, forecast_api.format(api_key, loc["lat"], loc["long"]))
        return json.loads(resp)


def format_weather(blob, loc, time):
    """Format the weather nicely."""
    w = {"loc": loc["addr"]}
    if time == "currently":
        summary = blob["currently"]["summary"]
        summary = summary[0] + summary[1:].lower()
        temp = blob["currently"]["temperature"]
        app_temp = blob["currently"]["apparentTemperature"]
        w["humidity"] = round(blob["currently"]["humidity"] * 100)
        wind = blob["currently"]["windSpeed"]
    else:
        summary = blob[time]['summary']
        temp = blob[time]['data'][0]['temperature']
        app_temp = blob[time]['data'][0]["apparentTemperature"]
        w["humidity"] = round(blob[time]['data'][0]['humidity'] * 100)
        wind = blob[time]['data'][0]["windSpeed"]

    w["summary"] = summary + "." if summary[-1] != "." else summary
    w["temp_f"] = round(temp)
    w["temp_c"] = round(to_celsius(temp))
    w["app_temp_f"] = round(app_temp)
    w["app_temp_c"] = round(to_celsius(app_temp))
    w["wind_mph"] = round(wind)
    w["wind_kph"] = round(wind*1.609)

    return "Weather in {loc}: {summary} {temp_f}˚F ({temp_c}˚C). Feels like {app_temp_f}˚F " \
           "({app_temp_c}˚C). Humidity: {humidity}%. Wind speed: {wind_mph}mph " \
           "({wind_kph}kph).".format(**w)


def to_celsius(temp):
    """Convert Fahrenheit to Celsius."""
    return (temp-32)*5/9