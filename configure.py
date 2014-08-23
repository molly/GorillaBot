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
        cursor = self.db_conn.cursor()
        try:
            cursor.execute('''UPDATE channels SET joined = 0''')
        except sqlite3.OperationalError as e:
            pass
        cursor.execute('''DROP TABLE IF EXISTS users_to_channels''')
        self.db_conn.commit()
        cursor.close()
        ans = ''
        while ans not in ["0", "1", "2", "3", "4"]:
            data = self.get_settings()
            if data is not None and len(data) > 0:
                print("Existing configurations:")
                for row in data:
                    print('\t' + row[0])
                print("\n[0] Load configuration\n[1] Create new configuration\n[2] View "
                      "configuration\n[3] Remove configuration\n[4] Exit")
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

    def get_settings(self):
        """Retrieve existing configurations, or create the table if it does not exist."""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute('''SELECT name FROM settings''')
        except sqlite3.OperationalError:
            # No settings table exists in the DB, so create one
            cursor.execute('''CREATE TABLE settings
                              (name TEXT NOT NULL PRIMARY KEY,
                               nick TEXT NOT NULL,
                               realname TEXT NOT NULL,
                               ident TEXT NOT NULL,
                               password TEXT)''')
            self.db_conn.commit()
            cursor.close()
            data = None
        else:
            data = cursor.fetchall()
            cursor.close()
        finally:
            # Create channels, users, and users_to_channels tables
            cursor = self.db_conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS channels
                              (chan_id INTEGER PRIMARY KEY,
                               name TEXT NOT NULL UNIQUE,
                               joined BOOLEAN NOT NULL CHECK(joined IN(0,1)),
                               setting TEXT,
                               FOREIGN KEY(setting) REFERENCES settings(name) ON DELETE CASCADE)
                               ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                              (user_id INTEGER PRIMARY KEY,
                               nick TEXT NOT NULL,
                               user TEXT,
                               host TEXT,
                               botop BOOLEAN NOT NULL CHECK(botop IN(0,1)),
                               setting TEXT,
                               FOREIGN KEY(setting) REFERENCES settings(name) ON DELETE CASCADE)
                               ''')
            cursor.execute('''CREATE TABLE users_to_channels
                              (user_id INTEGER,
                               chan_id INTEGER,
                               FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                               FOREIGN KEY(chan_id) REFERENCES channels(chan_id) ON DELETE CASCADE)
                               ''')
            self.db_conn.commit()
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
            nick = self.prompt("Nick", "GorillaBot")
            realname = self.prompt("Ident", "GorillaBot")
            ident = self.prompt("Realname", "GorillaBot")
            chans = self.prompt("Chans")
            botop = self.prompt("Bot operator(s)", '')
            password = self.prompt("Server password", hidden=True)
            chans = re.split(',? ', chans)
            botop = re.split(',? ', botop)
            self.display((name, nick, realname, ident, password), chans, botop)
            verify = input('Is this configuration correct? [y/n]: ').lower()
        self.save_config((name, nick, realname, ident, chans, botop, password))
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
                               setting TEXT,
                               FOREIGN KEY(setting) REFERENCES settings(name) ON DELETE CASCADE)
                               ''')
            cursor.execute('''DELETE FROM users WHERE setting = ?''', (name,))
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
            cursor.execute("SELECT * FROM settings WHERE name = ?",
                                (configuration,))
            data = cursor.fetchone()
            cursor.close()
            if data is not None:
                cursor = self.db_conn.cursor()
                cursor.execute('''SELECT name FROM channels WHERE setting = ?''',
                        (configuration,))
                channels = cursor.fetchall()
                cursor.close()
                channels = [x[0] for x in channels]
                cursor = self.db_conn.cursor()
                cursor.execute('''SELECT nick FROM users WHERE botop = 1 AND setting = ?''',
                        (configuration,))
                botops = cursor.fetchall()
                cursor.close()
                botops = [x[0] for x in botops]
                self.display(data, channels, botops)
                return (configuration, data, channels, botops)
            else:
                print("{0} is not the name of an existing configuration.".format(
                    configuration))

    def delete(self, name=None):
        """Delete a configuration."""
        if name is None:
            name = input("Please choose an existing configuration: ")
        cursor = self.db_conn.cursor()
        cursor.execute("DELETE FROM settings WHERE name = ?", (name,))
        self.db_conn.commit()
        cursor.close()

    def display(self, data, chans, botops):
        """Display a configuration."""
        chans = ", ".join(chans)
        botops = ", ".join(botops)
        password = "[hidden]" if data[4] else "[none]"
        print(
            "\n------------------------------\n Nickname: {0}\n Real "
            "name: {1}\n Identifier: {2}\n Channels: {3}\n Bot operator(s): {"
            "4}\n Server password: {5}\n------------------------------\n"
            .format(data[1], data[2], data[3], chans, botops, password))

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
                password = self.prompt("Server password", hidden=True)
                chans = re.split(',? ', chans)
                botop = re.split(',? ', botop)
                self.display((name, nick, realname, ident, password), chans,
                        botop)
                verify = input('Is this configuration correct? [y/n]: ').lower()
            self.delete(name)
            cursor = self.db_conn.cursor()
            cursor.execute('''DELETE FROM channels WHERE setting = ?''', (name,))
            cursor.execute('''DELETE FROM users WHERE setting = ?''', (name,))
            self.db_conn.commit()
            cursor.close()
            self.save_config((name, nick, realname, ident, chans, botop, password))

    def save_config(self, data):
        """Save changes to the configuration table."""
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO settings VALUES (?, ?, ?, ?, ?)''',
                       (data[0], data[1], data[2], data[3], data[6],))
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
                cursor.execute('''INSERT OR IGNORE INTO channels VALUES (NULL, ?, 0, ?)''',
                        (chan, data[0]))
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
