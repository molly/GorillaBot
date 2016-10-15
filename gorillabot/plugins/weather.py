# Copyright (c) 2013-2016 Molly White
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

    #-     !weather [--now|--week] location
    #-
    #- ```irc
    #- < GorillaWarfare> !weather boston
    #- < GorillaBot> Weather in Boston, MA, USA: Rain until tomorrow evening and breezy until
    #-               tomorrow morning. 51˚F (10˚C). Feels like 51˚F (10˚C). Humidity: 95%. Wind
    #-               speed: 23mph (38kph).
    #- < GorillaWarfare> !weather --now boston
    #- < GorillaBot> Weather in Boston, MA, USA: Light Rain and Breezy. 51˚F (10˚C). Feels like
    #-               51˚F (10˚C). Humidity: 96%. Wind speed: 25mph (40kph).
    #- < GorillaWarfare> !weather --week boston
    #- < GorillaBot> Weather in Boston, MA, USA: Light rain throughout the week, with temperatures
    #-               bottoming out at 53°F on Friday. 51–55˚F (11–13˚C).
    #- ```
    #-
    #- Provide weather information for the given location. Defaults to giving weather information
    #- about today. Given the `--now` parameter, this will give the current weather. Given the
    #- `--weekly` parameter, this will give the forecast for the week. Powered by Dark Sky.
    #- https://darksky.net/poweredby/.
    #-
    #- In order to provide weather information, you must provide a Forecast.io API key when
    #-  configuring the bot. You can get an API key by registering an email address at
    #-  https://darksky.net/dev/.

    api_key = m.bot.configuration["forecast"]
    if api_key:
        if len(m.line) <= 1:
            m.bot.private_message(m.location, "Please format this command as !weather ["
                                              "args] location")
        else:
            if any(s in m.line for s in ["--now", "-now", "-n"]):
                line = [word for word in m.line[1:] if word not in ["--now", "-now", "-n"]]
                loc = get_location(m, line)
                blob = get_weather(m, loc, api_key)
                msg = format_weather_now(blob, loc)
            elif any(s in m.line for s in ["--week", "-week", "-w"]):
                line = [word for word in m.line[1:] if word not in ["--week", "-week", "-w"]]
                loc = get_location(m, line)
                blob = get_weather(m, loc, api_key)
                msg = format_weather_weekly(blob, loc)
            else:
                loc = get_location(m, m.line[1:])
                blob = get_weather(m, loc, api_key)
                msg = format_weather(blob, loc)
            m.bot.private_message(m.location, msg)
    else:
        m.bot.logger.info("No Forecast.io API key recorded.")
        m.bot.private_message(m.location, "Ask a bot administrator to add a Forecast.io API key so "
                                          "you can use this command.")


def get_location(m, line):
    """Get the latitude, longitude, and well-formatted name of the given location."""
    google_api = "http://maps.googleapis.com/maps/api/geocode/json?address={}"
    loc = {}
    loc["name"] = " ".join(line)
    resp = get_url(m, google_api.format("+".join(line)))
    blob = json.loads(resp)
    if not blob["results"]:
        m.bot.private_message(m.location, "Could not find weather information for {}."
                              .format(" ".join(line)))
    else:
        loc["lat"] = blob['results'][0]['geometry']['location']['lat']
        loc["long"] = blob['results'][0]['geometry']['location']['lng']
        loc["addr"] = blob['results'][0]['formatted_address']
        return loc


def get_weather(m, loc, api_key):
    """Make the API call to get the weather."""
    if loc:
        m.bot.logger.info("Finding weather for {}.".format(loc["name"]))
        forecast_api = "https://api.darksky.net/forecast/{0}/{1},{2}?exclude=flags"
        resp = get_url(m, forecast_api.format(api_key, loc["lat"], loc["long"]))
        return json.loads(resp)


def format_weather(blob, loc):
    """Format the weather nicely."""
    w = dict(loc=loc["addr"])
    w["summary"] = blob["hourly"]['summary']
    temp = blob["hourly"]['data'][0]['temperature']
    app_temp = blob["hourly"]['data'][0]["apparentTemperature"]
    w["humidity"] = round(blob["hourly"]['data'][0]['humidity'] * 100)
    wind = blob["hourly"]['data'][0]["windSpeed"]

    w["temp_f"] = round(temp)
    w["temp_c"] = round(to_celsius(temp))
    w["app_temp_f"] = round(app_temp)
    w["app_temp_c"] = round(to_celsius(app_temp))
    w["wind_mph"] = round(wind)
    w["wind_kph"] = round(wind * 1.609)

    return "Weather in {loc}: {summary} {temp_f}˚F ({temp_c}˚C). Feels like {app_temp_f}˚F " \
           "({app_temp_c}˚C). Humidity: {humidity}%. Wind speed: {wind_mph}mph " \
           "({wind_kph}kph).".format(**w)


def format_weather_now(blob, loc):
    """Format the current weather nicely."""
    w = {"loc": loc["addr"]}
    summary = blob["currently"]["summary"]
    summary = summary[0] + summary[1:].lower()
    temp = blob["currently"]["temperature"]
    app_temp = blob["currently"]["apparentTemperature"]
    w["humidity"] = round(blob["currently"]["humidity"] * 100)
    wind = blob["currently"]["windSpeed"]

    w["summary"] = summary + "." if summary[-1] != "." else summary
    w["temp_f"] = round(temp)
    w["temp_c"] = round(to_celsius(temp))
    w["app_temp_f"] = round(app_temp)
    w["app_temp_c"] = round(to_celsius(app_temp))
    w["wind_mph"] = round(wind)
    w["wind_kph"] = round(wind * 1.609)

    return "Weather in {loc}: {summary} {temp_f}˚F ({temp_c}˚C). Feels like {app_temp_f}˚F " \
           "({app_temp_c}˚C). Humidity: {humidity}%. Wind speed: {wind_mph}mph " \
           "({wind_kph}kph).".format(**w)


def format_weather_weekly(blob, loc):
    """Format the weekly weather nicely."""
    w = {"loc": loc["addr"]}
    w["summary"] = blob["daily"]["summary"]
    min_temp = blob["daily"]["data"][0]["temperatureMin"]
    max_temp = blob["daily"]["data"][0]["temperatureMax"]

    w["min_temp_f"] = round(min_temp)
    w["min_temp_c"] = round(to_celsius(min_temp))
    w["max_temp_f"] = round(max_temp)
    w["max_temp_c"] = round(to_celsius(max_temp))

    return "Weather in {loc}: {summary} {min_temp_f}–{max_temp_f}˚F ({min_temp_c}–" \
           "{max_temp_c}˚C).".format(**w)


def to_celsius(temp):
    """Convert Fahrenheit to Celsius."""
    return (temp - 32) * 5 / 9
