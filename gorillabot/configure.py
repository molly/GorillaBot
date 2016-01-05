# Copyright (c) 2013-2016 Molly White
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

from getpass import getpass
import json
import logging
import os
import re


class Configurator(object):
    """Handles the configuration settings in the database."""

    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.abspath(os.path.join(self.base_path, "..", "config.json"))
        self.logger = logging.getLogger("GorillaBot")

    def configure(self):
        """Provide the user with prompts to interact with the configuration of the bot."""
        # Reset values from last time the bot was run
        self.reset()

        # Configure
        ans = ''
        while ans not in ["0", "1", "2", "3", "4"]:
            data = self.get_settings()
            if data is None:
                # File is poorly formatted and user doesn't want to overwrite
                return False
            if not data:
                # File contains no configs
                ans = ''
                while ans not in ["0", "1"]:
                    print("\n[0] Create new configuration\n[1] Exit")
                    ans = input("")
                    if ans == "0":
                        return self.create_new()
                    elif ans == "1":
                        return False
            elif data is not None:
                print("Existing configurations:")
                for key in data.keys():
                    print('\t' + key)
                print("\n[0] Load configuration\n[1] Create new configuration\n[2] View "
                      "configuration\n"
                      "[3] Remove configuration\n[4] Exit")
                ans = input("")
                if ans == "0":
                    return self.load_settings()
                elif ans == "1":
                    return self.create_new()
                elif ans == "2":
                    self.display()
                elif ans == "3":
                    self.delete()
                elif ans == "4":
                    return False
                ans = ''

    def reset(self):
        """Set all "joined" values to false for channels."""
        settings = self.get_settings()
        for config in settings.keys():
            for chan in settings[config]["chans"].keys():
                settings[config]["chans"][chan]["joined"] = False
            for op in settings[config]["botops"]:
                settings[config]["botops"][op] = {"user": "", "host": ""}
        self.save_config(settings)

    def get_settings(self):
        """Retrieve existing configurations, or create the config file if it does not exist."""
        try:
            with open(self.file_path, "r") as f:
                blob = json.load(f)
        except FileNotFoundError:
            self.logger.debug("No configuration file. Creating new one at {}."
                              .format(self.file_path))
            with open(self.file_path, "w") as f:
                json.dump({}, f)
                blob = {}
        except ValueError:
            overwrite = input("Configuration file is formatted incorrectly. Erase and create a new"
                              " one? [y/n] ")
            if overwrite.lower() == "y":
                self.logger.info("Overwrote incorrectly-formatted configuration file.")
                with open(self.file_path, "w") as f:
                    json.dump({}, f)
                    blob = {}
            else:
                return None
        return blob

    def create_new(self):
        """Create a new configuration."""
        existing = self.get_settings()
        verify = False
        while not verify:
            print('\n')
            name = ""
            while name == "":
                name = input("Unique name for this configuration: ")
                if name in existing.keys():
                    print('The name "{0}" is not unique.'.format(name))
                    name = ""
            settings = {name: {}}
            settings[name]["nick"] = self.prompt("Nick", "GorillaBot")
            settings[name]["realname"] = self.prompt("Ident", "GorillaBot")
            settings[name]["ident"] = self.prompt("Realname", "GorillaBot")
            chans = re.split(',? ', self.prompt("Channel(s)"))
            botops = re.split(',? ', self.prompt("Bot operator(s)", ''))
            settings[name]["password"] = self.prompt("Server password (optional)", hidden=True)
            settings[name]["youtube"] = self.prompt("YouTube API key (optional)", hidden=True)
            settings[name]["forecast"] = self.prompt("Forecast.io API key (optional)", hidden=True)
            settings[name]["chans"] = {}
            settings[name]["botops"] = {}
            for chan in chans:
                if chan:
                    settings[name]["chans"][chan] = {"joined": False, "settings": {}}
            for op in botops:
                if op:
                    settings[name]["botops"][op] = {"user": "", "host": ""}
            verify = self.verify(settings, name)
        new_settings = self.get_settings()
        new_settings.update(settings)
        self.save_config(new_settings)
        return name

    def load_settings(self):
        """Show a given configuration."""
        return self.display()

    def delete(self):
        """Delete a configuration."""
        settings = self.get_settings()
        name = input("Please choose an existing configuration: ")
        try:
            del settings[name]
            self.save_config(settings)
        except KeyError:
            print("No configuration named {}.".format(name))

    def display(self, settings = None, name = None):
        """Display a configuration."""
        if not settings:
            settings = self.get_settings()
            name = ""
            while name == "":
                name = input("Please choose an existing configuration: ")
                if name not in settings.keys():
                    print("No configuration named {}.".format(name))
                    name = ""
        chans = ", ".join(settings[name]["chans"].keys())
        botops = ", ".join(settings[name]["botops"].keys())
        password = "[hidden]" if settings[name]["password"] else "[none]"
        youtube = "[hidden]" if settings[name]["youtube"] else "[none]"
        forecast = "[hidden]" if settings[name]["forecast"] else "[none]"
        print(
            "\n------------------------------\n Nickname: {0}\n Real name: {1}\n Identifier: {2}\n"
            " Channels: {3}\n Bot operator(s): {4}\n Server password: {5}\n YouTube API key: {6}\n"
            " Forecast.io API key: {7}\n------------------------------\n"
            .format(settings[name]["nick"], settings[name]["realname"], settings[name]["ident"],
                    chans, botops, password, youtube, forecast))
        return name

    def verify(self, settings, name):
        """Verify a configuration, and make changes if needed."""
        verify = ''
        while verify != 'y' and verify != 'n':
            self.display(settings, name)
            verify = input('Is this configuration correct? [y/n]: ').lower()
        return True if verify.lower() == 'y' else False

    def save_config(self, new_settings):
        """Save changes to the configuration table."""
        with open(self.file_path, "w") as f:
            json.dump(new_settings, f, indent=4)

    def prompt(self, field, default=None, hidden=False):
        """Prompt a user for input, displaying a default value if one exists."""
        if default:
            field += " [DEFAULT: {}]".format(default)
        field += ": "
        if not hidden:
            answer = input(field)
        else:
            answer = getpass(field)
        if default is not None and answer == '':
            return default
        return answer
