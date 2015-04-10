# GorillaBot
GorillaBot is an easily-extensible IRC bot written in Python.

__Author:__ Molly White<br />
__License:__ [MIT](http://opensource.org/licenses/MIT)<br/>
__Status:__ Stable<br />
__Version:__ 2.0<br />
__Python version:__ 3.4+

## Installation
_Download code from the `master` branch. Code in the `development` or other branches is often
incomplete and nonfunctional._

The bot is available on [PyPI](https://pypi.python.org/pypi/gorillabot), so it can be installed 
with `pip install gorillabot` or `easy_install gorillabot`.

Alternatively, install the bot from source:

1. Run `python3 bot.py` from the source directory.
2. Configure the bot when prompted. If you already have already configured the bot, you can use
that configuration or create a new one.
3. Once the bot has successfully connected, command the bot via IRC. A number of commands are
marked as admin-only, and are only available to bot operators. All commands are outlined in the 
[documentation](http://molly.github.io/GorillaBot/).

## Documentation
GorillaBot generates its own plugin [documentation](http://molly.github.io/GorillaBot/). If you
add a plugin, please document it by writing usage notes in comments beginning with `#-`. You can
see an example in the
[link command](https://github.com/molly/GorillaBot/blob/master/plugins/link.py#L27). Note that
you do not need to specify if a command is admin-only or not; this is determined from the decorator.
