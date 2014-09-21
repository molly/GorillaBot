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

from getpass import getpass
import logging
import re
import sqlite3


class Configurator(object):
    """Handles the configuration settings in the database."""

    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.logger = logging.getLogger("GorillaBot")

    def configure(self):
        """Provide the user with prompts to interact with the configuration of the bot."""

        # If there's an existing channels table, set joined to false for all channels
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''UPDATE channels SET joined = 0''')
            self.db_conn.commit()
            cursor.close()
        except sqlite3.OperationalError:
            pass

        # Drop the users_to_channels table if it exists
        cursor = self.db_conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS users_to_channels''')
        self.db_conn.commit()
        cursor.close()

        # Create all the tables that we need, if we need them
        self.create_tables()

        # Prompt user for input
        ans = ''
        while ans not in ["0", "1", "2", "3", "4"]:
            data = self.get_settings()
            if data is not None and len(data) > 0:
                print("Existing configurations:")
                for row in data:
                    print('\t' + row[0])
                print(
                    "\n[0] Load configuration\n[1] Create new configuration\n[2] View "
                    "configuration\n"
                    "[3] Remove configuration\n[4] Exit")
                ans = input("")
                if ans == "0":
                    return self.load_settings()
                elif ans == "1":
                    return self.create_new()
                elif ans == "2":
                    self.view()
                elif ans == "3":
                    self.delete()
                elif ans == "4":
                    return False
                ans = ''
            else:
                ans = ''
                while ans not in ["0", "1"]:
                    print("\n[0] Create new configuration\n[1] Exit")
                    ans = input("")
                    if ans == "0":
                        return self.create_new()
                    elif ans == "1":
                        return False

    def create_tables(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS configs
                (name TEXT NOT NULL PRIMARY KEY,
                 nick TEXT NOT NULL,
                 realname TEXT NOT NULL,
                 ident TEXT NOT NULL,
                 password TEXT,
                 youtube TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS channels
              (chan_id INTEGER PRIMARY KEY,
               name TEXT NOT NULL,
               joined BOOLEAN NOT NULL CHECK(joined IN(0,1)),
               config TEXT,

               FOREIGN KEY(config) REFERENCES configs(name) ON DELETE CASCADE,
               UNIQUE(name, config) ON CONFLICT REPLACE)
               ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
              (user_id INTEGER PRIMARY KEY,
               nick TEXT NOT NULL,
               user TEXT,
               host TEXT,
               botop BOOLEAN NOT NULL CHECK(botop IN(0,1)),
               config TEXT,
               FOREIGN KEY(config) REFERENCES configs(name) ON DELETE CASCADE)
               ''')
        cursor.execute('''CREATE TABLE users_to_channels
              (user_id INTEGER,
               chan_id INTEGER,
               FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
               FOREIGN KEY(chan_id) REFERENCES channels(chan_id) ON DELETE CASCADE)
               ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings
              (setting TEXT,
               value TEXT,
               chan_id INTEGER,
               FOREIGN KEY(chan_id) REFERENCES channels(chan_id) ON DELETE CASCADE,
               UNIQUE(setting, chan_id) ON CONFLICT REPLACE)
               ''')
        self.db_conn.commit()
        cursor.close()

    def get_settings(self):
        """Retrieve existing configurations, or create the table if it does not exist."""
        cursor = self.db_conn.cursor()
        cursor.execute('''SELECT name FROM configs''')
        data = cursor.fetchall()
        cursor.close()
        return data

    def create_new(self):
        """Create a new configuration."""
        verify = ''
        while verify != 'y':
            print('\n')
            name = ""
            while name == "":
                name = input("Unique name for this configuration: ")
                cursor = self.db_conn.cursor()
                cursor.execute('''SELECT * FROM configs WHERE name = ?''', (name,))
                data = cursor.fetchone()
                cursor.close()
                if data:
                    print('The name "{0}" is not unique.'.format(name))
                    name = ""
            nick = self.prompt("Nick", "GorillaBot")
            realname = self.prompt("Ident", "GorillaBot")
            ident = self.prompt("Realname", "GorillaBot")
            chans = self.prompt("Chans")
            botop = self.prompt("Bot operator(s)", '')
            password = self.prompt("Server password (optional)", hidden=True)
            youtube = self.prompt("YouTube API key (optional)", hidden=True)
            chans = re.split(',? ', chans)
            botop = re.split(',? ', botop)
            self.display((name, nick, realname, ident, password, youtube), chans, botop)
            verify = input('Is this configuration correct? [y/n]: ').lower()
        self.save_config((name, nick, realname, ident, chans, botop, password, youtube))
        return name

    def load_settings(self):
        """Show a given configuration, and allow the user to modify it if needed."""
        while True:
            name, data, channels, botops = self.view()
            cursor = self.db_conn.cursor()
            self.db_conn.commit()
            cursor.close()
            cursor = self.db_conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                (user_id INTEGER PRIMARY KEY,
                 nick TEXT NOT NULL,
                 user TEXT,
                 host TEXT,
                 botop BOOLEAN NOT NULL CHECK(botop IN(0,1)),
                 config TEXT,
                 FOREIGN KEY(config) REFERENCES configs(name) ON DELETE CASCADE)
                 ''')
            cursor.execute('''DELETE FROM users WHERE config = ?''', (name,))
            self.db_conn.commit()
            cursor.close()
            if botops != ['']:
                cursor = self.db_conn.cursor()
                for op in botops:
                    cursor.execute('''INSERT INTO users VALUES (NULL, ?, NULL, NULL, 1, ?)''',
                                   (op, name))
                self.db_conn.commit()
                cursor.close()
            self.verify(data, channels, botops)
            return name

    def view(self):
        """Open a configuration for viewing."""
        while True:
            configuration = input("Please choose an existing configuration: ")
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT * FROM configs WHERE name = ?", (configuration,))
            data = cursor.fetchone()
            cursor.close()
            if data is not None:
                cursor = self.db_conn.cursor()
                cursor.execute('''SELECT name FROM channels WHERE config = ?''', (configuration,))
                channels = cursor.fetchall()
                cursor.close()
                channels = [x[0] for x in channels]
                cursor = self.db_conn.cursor()
                cursor.execute('''SELECT nick FROM users WHERE botop = 1 AND config = ?''',
                               (configuration,))
                botops = cursor.fetchall()
                cursor.close()
                botops = [x[0] for x in botops]
                self.display(data, channels, botops)
                return (configuration, data, channels, botops)
            else:
                print("{0} is not the name of an existing configuration.".format(configuration))

    def delete(self, name=None):
        """Delete a configuration."""
        if name is None:
            name = input("Please choose an existing configuration: ")
        cursor = self.db_conn.cursor()
        cursor.execute("DELETE FROM configs WHERE name = ?", (name,))
        self.db_conn.commit()
        cursor.close()

    def display(self, data, chans, botops):
        """Display a configuration."""
        chans = ", ".join(chans)
        botops = ", ".join(botops)
        password = "[hidden]" if data[4] else "[none]"
        youtube = "[hidden]" if data[5] else "[none]"
        print(
            "\n------------------------------\n Nickname: {0}\n Real name: {1}\n Identifier: {2}\n"
            " Channels: {3}\n Bot operator(s): {4}\n Server password: {5}\nYouTube API key: {6}\n"
            "------------------------------\n".format(data[1], data[2], data[3], chans, botops,
                                                      password, youtube))

    def verify(self, data, chans, botops):
        """Verify a configuration, and make changes if needed."""
        verify = input('Is this configuration correct? [y/n]: ').lower()
        if verify == 'y':
            return
        else:
            verify = ''
            while verify != 'y':
                print('\n')
                name = data[0]
                nick = self.prompt("Nick", data[1])
                realname = self.prompt("Ident", data[2])
                ident = self.prompt("Realname", data[3])
                chans = self.prompt("Chans", ", ".join(chans))
                botop = self.prompt("Bot operator(s)", ", ".join(botops))
                password = self.prompt("Server password (optional)", hidden=True)
                youtube = self.prompt("YouTube API key (optional)", hidden=True)
                chans = re.split(',? ', chans)
                botop = re.split(',? ', botop)
                self.display((name, nick, realname, ident, password, youtube), chans, botop)
                verify = input('Is this configuration correct? [y/n]: ').lower()
            self.delete(name)
            cursor = self.db_conn.cursor()
            cursor.execute('''DELETE FROM channels WHERE config = ?''', (name,))
            cursor.execute('''DELETE FROM users WHERE config = ?''', (name,))
            self.db_conn.commit()
            cursor.close()
            self.save_config((name, nick, realname, ident, chans, botop, password, youtube))

    def save_config(self, data):
        """Save changes to the configuration table."""
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO configs VALUES (?, ?, ?, ?, ?, ?)''',
                       (data[0], data[1], data[2], data[3], data[6], data[7],))
        self.db_conn.commit()
        cursor.close()
        if type(data[4]) is str:
            channels = re.split(',? ', data[4])
        else:
            channels = data[4]
        if type(data[5]) is str:
            botops = re.split(',? ', data[5])
        else:
            botops = data[5]
        cursor = self.db_conn.cursor()
        if channels != ['']:
            for chan in channels:
                if chan[0] != "#":
                    chan = "#" + chan
                cursor.execute('''INSERT INTO channels VALUES (NULL, ?, 0, ?)''', (chan, data[0]))
        self.db_conn.commit()
        cursor.close()
        cursor = self.db_conn.cursor()
        if botops != ['']:
            for op in botops:
                cursor.execute('''INSERT INTO users VALUES (NULL, ?, NULL, NULL, 1, ?)''',
                               (op, data[0]))
        self.db_conn.commit()
        cursor.close()

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
