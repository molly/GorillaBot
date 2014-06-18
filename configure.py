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
                    self.load_settings()
                    return True
                elif ans == "1":
                    self.create_new()
                    return True
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
                        self.create_new()
                    elif ans == "1":
                        return False

    def get_settings(self):
        """Retrieve existing configurations, or create the table if it does not exist."""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute('''SELECT name FROM settings''')
        except sqlite3.OperationalError as e:
            # No settings table exists in the DB, so create one
            cursor.execute('''CREATE TABLE settings
                              (name TEXT NOT NULL PRIMARY KEY,
                               host TEXT NOT NULL,
                               port INTEGER NOT NULL,
                               nick TEXT NOT NULL,
                               realname TEXT NOT NULL,
                               ident TEXT NOT NULL,
                               password TEXT,
                               wait BOOLEAN NOT NULL CHECK(wait IN(0,1)))''')
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
                               nick TEXT NOT NULL UNIQUE,
                               user TEXT,
                               host TEXT,
                               botop BOOLEAN NOT NULL CHECK(botop IN(0,1)))''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS users_to_channels
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
            host = self.prompt("Host", "chat.freenode.net")
            port = self.prompt("Port", 6667)
            nick = self.prompt("Nick", "GorillaBot")
            realname = self.prompt("Ident", "GorillaBot")
            ident = self.prompt("Realname", "GorillaBot")
            chans = self.prompt("Chans")
            botop = self.prompt("Bot operator(s)", '')
            password = self.prompt("Server password", hidden=True)
            wait = ""
            while wait != 'y' and wait != 'n':
                wait = self.prompt("Wait to join before entering channels? [y/n]", 'n')
                wait.lower()
            wait = 0 if wait == 'n' else 1
            chans = re.split(',? ', chans)
            botop = re.split(',? ', botop)
            self.display((name, host, port, nick, realname, ident, password, wait), chans, botop)
            verify = input('Is this configuration correct? [y/n]: ').lower()
        self.save_config((name, host, port, nick, realname, ident, chans, botop, password, wait))

    def load_settings(self):
        """Show a given configuration, and allow the user to modify it if needed."""
        while True:
            data, channels, botops = self.view()
            self.verify(data, channels, botops)
            return

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
                channels = [x[0] for x in channels]
                cursor.close()
                cursor = self.db_conn.cursor()
                cursor.execute('''SELECT nick FROM users WHERE botop = 1''')
                botops = cursor.fetchall()
                botops = [x[0] for x in botops]
                self.display(data, channels, botops)
                return (data, channels, botops)
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
        password = "[hidden]" if data[6] else "[none]"
        wait = "n" if data[7] else "y"
        print(
            "\n------------------------------\n Host: {0}\n Port: {1}\n Nickname: {2}\n Real "
            "name: {3}\n Identifier: {4}\n Channels: {5}\n Bot operator(s): {"
            "6}\n Server password: {7}\n Wait to join?: {8}\n------------------------------\n"
            .format(data[1], data[2], data[3], data[4], data[5], chans, botops, password, wait))

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
                host = self.prompt("Host", data[1])
                port = self.prompt("Port", data[2])
                nick = self.prompt("Nick", data[3])
                realname = self.prompt("Ident", data[4])
                ident = self.prompt("Realname", data[5])
                chans = self.prompt("Chans", ", ".join(chans))
                botop = self.prompt("Bot operator(s)", ", ".join(botops))
                password = self.prompt("Server password", hidden=True)
                wait = ""
                while wait != 'y' and wait != 'n':
                    wait = 'y' if data[7] == 1 else 'n'
                    wait = self.prompt("Wait to join before entering channels? [y/n]", wait)
                    wait.lower()
                wait = 0 if wait == 'n' else 1
                chans = re.split(',? ', chans)
                botop = re.split(',? ', botop)
                self.display((name, host, port, nick, realname, ident, password, wait), chans,
                        botop)
                verify = input('Is this configuration correct? [y/n]: ').lower()
            self.delete(name)
            cursor = self.db_conn.cursor()
            cursor.execute('''DELETE FROM channels WHERE setting = ?''', (name,))
            self.save_config((name, host, port, nick, realname, ident, chans, botop, password,
                             wait))

    def save_config(self, data):
        """Save changes to the configuration table."""
        cursor = self.db_conn.cursor()
        cursor.execute('''INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (data[0], data[1], data[2], data[3], data[4], data[5], data[8], data[9]))
        if type(data[6]) is str:
            channels = re.split(',? ', data[6])
        else:
            channels = data[6]
        if type(data[7]) is str:
            botops = re.split(',? ', data[7])
        else:
            botops = data[7]
        cursor.execute('''DELETE FROM users''')
        if channels != ['']:
            for chan in channels:
                if chan[0] != "#":
                    chan = "#" + chan
                cursor.execute('''INSERT OR IGNORE INTO channels VALUES (NULL, ?, 0, ?)''',
                        (chan, data[0]))
        if botops != ['']:
            for op in botops:
                cursor.execute('''INSERT INTO users VALUES (NULL, ?, NULL, NULL, 1)''', (op,))
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
