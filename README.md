# GorillaBot
GorillaBot is an IRC bot framework written in Python. The bot is initiated from the command line. Once it is connected, it receives [its commands](https://github.com/mollywhite/GorillaBot/blob/master/docs/commands.md) through IRC. Because I'm writing the framework mainly for use in a channel frequented by Wikipedia editors, there are a number of Wikipedia-specific commands.

Although I wrote the framework to run _AlfredBot_, a bot specific to an IRC channel I use frequently, it is easily-configurable to run any bot you like. It will include some optional modules, and any extra functionality can be added by forking the code. You can see my ideas for the bot [here](https://github.com/mollywhite/GorillaBot/blob/master/docs/todo.md). Feel free to make your own suggestions!

__Author:__ Molly White<br />
__License:__ [MIT](http://opensource.org/licenses/MIT)<br/>
__Status:__ Unstable

## Installation
_Download code from the master branch. Code in the development branch is often incomplete._

1. Run `python3 Commander.py` from the source directory. This will step you through creating a configuration file if you don't have one already. If you already have a configuration file, it will verify its validity and check if you'd like to change it.
2. Enter any information in the command line prompts.
3. Once the command line logger displays that you have successfully connected, command the bot using [these commands](https://github.com/mollywhite/GorillaBot/blob/master/docs/commands.md) on IRC.


## Credit
Thank you to [Ben Kurtovic](https://github.com/earwig) for his lovely [EarwigBot](https://github.com/earwig/earwigbot), which provided a good example and some of the code for this bot.
