# GorillaBot
GorillaBot is an IRC bot framework written in Python. The bot is initiated from the command line. Once it is connected, it receives [its commands](https://github.com/mollywhite/GorillaBot/blob/master/docs/commands.md) through IRC. Because I'm writing the framework mainly for use in a channel frequented by Wikipedia editors, there are a number of Wikipedia-specific commands.

Although I wrote the framework to run a bot specific to an IRC channel on the Freenode network, it is easily configurable and extensible so you can create any bot you like. It will include some optional modules, and any extra functionality can be added by forking the code. Feel free to suggest additional functionality!

__Author:__ Molly White<br />
__License:__ [MIT](http://opensource.org/licenses/MIT)<br/>
__Status:__ Unstable<br />
__Version:__ 2.0

## Installation
_Download code from the `master` branch. Code in the `rewrite` branch is often incomplete and non-functional._

1. Run `python3 commander.py` from the source directory. This will step you through creating a configuration file if you don't have one already. If you already have a configuration file, you can use that same configuration file or create a new one.
2. Enter any information in the command line prompts.
3. Once the command line logger displays that you have successfully connected, command the bot using [these commands](https://github.com/mollywhite/GorillaBot/blob/master/docs/commands.md) on IRC.


## Credit
Thank you to [Ben Kurtovic](https://github.com/earwig) for his lovely [EarwigBot](https://github.com/earwig/earwigbot), which provided a good example and some of the code for this bot.
