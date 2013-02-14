#Adding plugins

GorillaBot was designed to be easily extensible. Adding commands is relatively simple:

1. Either edit an existing `.py` file in the `/plugins` directory, or create a new file.
2. If you choose to add a new file, append the file name (sans the file extension) to the `__all__` variable in the `__init__.py` file in `/plugins`.
3. Create the command function in the following format: `def [commandname](sender, command_type, line).

##Notes

IRC messages are received in raw form as:

    :<prefix> <command> <params> :<trailing>
    
So, for example:

    :GorillaWarfare!~wikipedia/GorillaWarfare PRIVMSG #channelname :Hello world!

This is obviously a bit unweildy, so the CommandManager formats the message before sending it to the command to prevent each command having to do this individually.

###Command arguments

####Sender
`sender` is the name of the user, stripped of the cloak and other unnecessary characters. From the example above, the CommandManager would assign `sender` as `GorillaWarfare`.

####Command type
`command_type` is the way in which the bot received the command. As discussed in the [command documentation](https://github.com/mollywhite/GorillaBot/blob/development/docs/commands.md), the bot can receive messages in any of three ways. The bot records the type of command in case you wish to restrict which type triggers a command. The bot actually records how it receives the message as one of _four_ types:

1. `private`: The commanding user sent the command to the bot via a private message (using, for example, `\msg GorillaBot command`).

2. `direct`: The commanding user addressed the command to the bot in a public channel by using the bot's nick (for example, `GorillaBot: command`).

3. `exclamation`: The commanding user preceded a command in a public channel with an exclamation point _anywhere in the message_ (for example, ``You should perform !command``).

4. `exclamation_first`: The commanding user preceded a command in a public channel with an exclamation point, and this command was the first word in the message. The example above would not be categorized as this type because `!command` was not the first word in the message. A message like `!command should be performed` would, however, be categorized as this type.

####Line
The `line` argument is the rest of the message: the trailing bit, but not the prefix, command, or parameters. From the example above, `line` would be `Hello world!`. You'll notice that it is not `:Hello world!` -- the preceding colon is also stripped from the message. Also keep in mind that if a user formats a command as `!link [[this article]]`, `line` consists of `!link [[this article]]`, not just `[[this article]]`. Removal of the command from the line and identification of any specific command parameters must be performed in the command body.
