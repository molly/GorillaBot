# Commanding the bot

The bot receives commands in one of three ways:

1. Detecting a word preceded by an exclamation point: `!command`<br/>
2. Receiving a message addressed to it directly: `GorillaBot: command` or `GorillaBot: !command`<br/>
3. Receiving a command in a private message: `/msg GorillaBot command`

In the examples below, I use the `!command` syntax, but the other two would work equally well.

##Commands
###[All users](#all-user-commands)
* [adminlist](#adminlist)
* [commands](#commands-1)
* [emergencyshutoff](#emergencyshutoff)
* [flirt](#flirt)
* [help](#help)
* [hug](#hug)
* [link](#link)
* [user](#user)
* [usertalk](#usertalk)

###[Bot admins only](#bot-admin-commands)
* [addadmin](#addadmin)
* [join](#join)
* [part](#part)
* [quit](#quit)
* [removeadmin](#removeadmin)

## All-user commands ##
### Adminlist ###
	!adminlist
	
Provides a list of the bot administrators.

```irc
<GorillaWarfare> !adminlist
<GorillaBot> My bot admin is GorillaWarfare.
```

### Commands ###
    !commands
    
If this command is sent as a private message to the bot, it will respond with a list of available commands. If it is sent publicly, it will respond with a link to this page only (to avoid a lengthy reply.)

__Private__
```irc
<GorillaWarfare> !commands
<GorillaBot> I know the following commands: commands, help, hug, link, user,
             usertalk. For further documentation, see http://git.io/pNQS6g
```

__Public__
```irc
<GorillaWarfare> !commands
<GorillaBot> Documentation of my commands is available at
             http://git.io/pNQS6g.
```

### Emergencyshutoff ###
	!emergencyshutoff
A sort of "big red button" for the bot. If the bot starts malfunctioning, a user can give this command to shut off the bot. This command should be disabled in large channels or in case of abuse.

### Flirt ###
	!flirt [user]
Flirts with the specified user. If no user is specified, it flirts at no one in particular.

```irc
<GorillaWarfare> !flirt GorillaWarfare
<GorillaBot> GorillaWarfare: What's your sign?
```

### Help ###
    !help
    
Prints a help message identifying the bot, telling the user how to view the command list, and directing them to this page.

```irc
<GorillaWarfare> !help
<GorillaBot> Hello, I'm your friendly neighborhood GorillaBot!
             I perform a number of commands that you can view by typing !commands.
             Alternatively, you can see my documentation at http://git.io/pNQS6g.
```

### Hug ###
	!hug [user]
Hugs the specified user. If no user is specified, the bot hugs the whole channel.

```irc
<GorillaWarfare> !hug GorillaWarfare
*GorillaBot glomps GorillaWarfare
<GorillaWarfare> !hug
*GorillaBot distributes hugs evenly among the channel
```

### Link ###
    !link [[Article]]
    !link [[Article#Section]]
    !link {{Template}}

Provide a link to a Wikipedia article.
    
```irc
<GorillaWarfare> !link [[Hello World]]
<GorillaBot> http://en.wikipedia.org/wiki/Hello_World
<GorillaWarfare> !link {{Welcome}}
<GorillaBot> http://en.wikipedia.org/wiki/Template:Welcome
```

### User ###
    !user Username
    !user [[Username]]
    
Provide a link to a Wikipedia user page.

```irc
<GorillaWarfare> !user GorillaWarfare
<GorillaBot> http://en.wikipedia.org/wiki/User:GorillaWarfare
```
    
### Usertalk ###
	!usertalk Username
    !usertalk [[Username]]
    
Provide a link to a Wikipedia user talk page.

```irc

<GorillaWarfare> !usertalk GorillaWarfare
<GorillaBot> http://en.wikipedia.org/wiki/User_talk:GorillaWarfare
```

## Bot admin commands ##

### Addadmin ###
    !addadmin user

Adds the user to the list of bot administrators.

### Join ###
    !join #channel
    
Joins the specified channel (or list of channels). Channels must be preceded with a pound sign, or the bot will ignore them.

### Part ###
	!part #channel

Parts from the specified channel (or list of channels).

### Quit ###
	!quit
	!shutdown
	
The bot gracefully exits and shuts down completely.

### Removeadmin ###
	!removeadmin user

Removes the user from the list of bot administrators. If you are the only administrator and you attempt to remove yourself from the list, the bot will ask you to add someone else before doing so.
