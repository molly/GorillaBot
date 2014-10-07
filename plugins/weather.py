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
            m.bot.private_message(m.location, "Please format this command as !weather [location]")
        else:
            m.bot.logger.info("Finding weather for {}.".format(" ".join(m.line[1:])))
            google_api = "http://maps.googleapis.com/maps/api/geocode/json?address={}"
            forecast_api = "https://api.forecast.io/forecast/{0}/{1},{2}?exclude=currently," \
                           "minutely,daily,alerts,flags"
            loc = quote("+".join(m.line[1:]))
            resp = get_url(m, google_api.format(loc))
            blob = json.loads(resp)
            lat = blob['results'][0]['geometry']['location']['lat']
            long = blob['results'][0]['geometry']['location']['lng']
            addr = blob['results'][0]['formatted_address']
            resp = get_url(m, forecast_api.format(api_key, lat, long))
            blob = json.loads(resp)
            summary = blob['hourly']['summary']
            temp = round(blob['hourly']['data'][0]['temperature'])
            humidity = round(blob['hourly']['data'][0]['humidity'] * 100)
            weather = "Weather in {0}: {1} {2}˚F ({3}˚C). Humidity: {4}%."\
                .format(addr, summary, str(temp), str(round((temp - 32)*5/9)), str(humidity))
            m.bot.private_message(m.location, weather)
    else:
        m.bot.logger.info("No Forecast.io API key recorded.")