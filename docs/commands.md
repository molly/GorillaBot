# Commanding the bot

These are the commands that are available to all users.

The bot receives commands in one of three ways:

1. Detecting a word preceded by an exclamation point: `!command`<br/>
2. Receiving a message addressed to it directly: `GorillaBot: command` or `GorillaBot: !command`<br/>
3. Receiving a command in a private message: `/msg GorillaBot command`

In the examples below, I use the `!command` syntax, but the other two would work equally well.

##Commands

### admincommands
    !admincommands
    !admincommandlist

Say the available admin-only commands. This does not display command aliases.

### adminlist
    !adminlist

Say the current bot operators.

### commands
    !commands
    !commandlist

Say the available admin-only commands. This does not display command aliases.

### link
    !link [url]

Provide information about the given link. By default it formats links as "Link: - [page title]", but it provides richer information about the following domains:

* twitch.tv
* youtube.com
* imgur.com
* reddit.com
    
#### Settings
* `auto` - All links entered in the chat will be parsed, regardless of whether they're prefaced with `!link`.
