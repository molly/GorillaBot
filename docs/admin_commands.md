# Commanding the bot

These are the commands that are only available to users specified as bot admins.

The bot receives commands in one of three ways:

1. Detecting a word preceded by an exclamation point: `!command`<br/>
2. Receiving a message addressed to it directly: `GorillaBot: command` or `GorillaBot: !command`<br/>
3. Receiving a command in a private message: `/msg GorillaBot command`

In the examples below, I use the `!command` syntax, but the other two would work equally well.

##Commands
* [join](#join)

### join
    !join #channel
Joins the specified channel. Only joins one channel at a time.

### part
    !part [#channel]
Parts from the specified channel, or the current channel if unspecified. Only parts from one channel at a time.
