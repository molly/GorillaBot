#Adding plugins

GorillaBot was designed to be easily extensible. Adding commands is relatively simple:

1. Either edit an existing `.py` file in the `/plugins` directory, or create a new file. You can have more than one function per `.py` file; I've chosen to group some of the bot's commands for readability.
2. If you choose to add a new file, append the file name (sans the file extension) to the `__all__` variable in the `__init__.py` file in `/plugins`.
3. Create the command function in the following format: `def [commandname](c, channel, command_type, line)`.

When the bot is initialized, it will look through each `.py` file in the `/plugins` directory and create a list of every function in each file. This list of functions becomes the bot's master list of commands.

##Notes

IRC messages are received in raw form as:

    :<prefix> <command> <params> :<trailing>
    
So, for example:

    :GorillaWarfare!~wikipedia/GorillaWarfare PRIVMSG #channelname :Hello world!

This is obviously a bit unwieldy, so the CommandManager does some message parsing before sending the message in its full form to the command.

###Command arguments

####c
`c` is an instance of the `CommandManager()` class. It allows access to necessary CommandManager functions (`get_sender`, `get_message`, `throttle`, etc.), as well as access to the `Connection` class.

####Channel
`channel` is the source of the command. If the command was sent to the bot publicly, this is the channel from which it was sent. If the command was sent via a private message, this is the nick of the sender.

####Command type
`command_type` is the way in which the bot received the command. As discussed in the [command documentation](https://github.com/mollywhite/GorillaBot/blob/development/docs/commands.md), the bot can receive messages in any of three ways. The bot records the type of command in case you wish to restrict which type triggers a command. The bot actually records how it receives the message as one of _five_ types:

1. `private`: The commanding user sent the command to the bot via a private message (using, for example, `\msg GorillaBot command`).

2. `direct`: The commanding user addressed the command to the bot in a public channel by using the bot's nick (for example, `GorillaBot: command`).

3. `exclamation`: The commanding user preceded a command in a public channel with an exclamation point _anywhere in the message_ (for example, ``You should perform !command``).

4. `exclamation_first`: The commanding user preceded a command in a public channel with an exclamation point, and this command was the first word in the message. The example above would not be categorized as this type because `!command` was not the first word in the message. A message like `!command should be performed` would, however, be categorized as this type.

5. `regex`: The message contained a match to a regex pattern in the `check_regex` function in the CommandManager. The bot can respond to messages that are not addressed to it specifically, but be _very_ careful with this. These types of commands should almost always be throttled to avoid spamming the channel.

####Line
The `line` argument is the message, formatted as a string. This contains the entire message (prefix, command, params, and trailing) and must be split within the command if any information is desired. Although this is perhaps more work in an individual command, it prevents the need to pass many arguments to each command without using the majority. The `get_sender` and `get_message` functions in the CommandManager provide an easy way of pulling the username of the sender and the trailing message out of the line.
