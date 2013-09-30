# Commanding the bot

These are the commands that are available to bot administrators only.

The bot receives commands in one of three ways:

1. Detecting a word preceded by an exclamation point: `!command`<br/>
2. Receiving a message addressed to it directly: `GorillaBot: command` or `GorillaBot: !command`<br/>
3. Receiving a command in a private message: `/msg GorillaBot command`

In the examples below, I use the `!command` syntax, but the other two would work equally well.

##Commands
* [join](#join)
* [leave](#part)
* [part](#part)

### join ###
    !join #channel
Joins the bot to the specified channel. Takes one channel at a time, requires the leading `#`.

### part ###
**Aliases:** `leave`

    !part #channel
    !leave #channel
Parts the bot from the specified channel. Takes one channel at a time, requires the leading `#`.

