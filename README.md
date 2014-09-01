# GorillaBot
GorillaBot is an IRC bot framework written in Python. The bot is initiated from the command line. Once it is connected, it receives [its commands](https://github.com/mollywhite/GorillaBot/blob/master/docs/commands.md) through IRC. Because I'm writing the framework mainly for use in a channel frequented by Wikipedia editors, there are a number of Wikipedia-specific commands.

__Author:__ Molly White<br />
__License:__ [MIT](http://opensource.org/licenses/MIT)<br/>
__Status:__ Stable<br />
__Version:__ 2.0

## Installation
_Download code from the `master` branch. Code in the `development` branch is often incomplete and non-functional._

1. Run `python3 bot.py` from the source directory. This will step you through configuring the bot. If you already have already configured the bot, you can use that configuration or create a new one.
2. Enter any information when prompted.
3. Once the bot has successfully connected, command the bot via IRC. There are also a number of admin commands available to bot operators. These are outlined in the [documentation](http://molly.github.io/GorillaBot/).
