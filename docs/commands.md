# Commanding the bot

The bot receives commands in one of three ways:

1. Detecting a word preceded by an exclamation point: `!command`<br/>
2. Receiving a message addressed to it directly: `GorillaBot: command` or `GorillaBot: !command`<br/>
3. Receiving a command in a private message: `/msg GorillaBot command`

In the examples below, I use the `!command` syntax, but the other two would work equally well.

##Commands
* [adminlist](#adminlist)
* [commands](#commands-1)
* [emergencyshutoff](#emergencyshutoff)
* [flirt](#flirt)
* [help](#help)
* [hug](#hug)
* [lang] (#lang)
* [link](#link)
* [notify] (#notify)
* [reverse] (#reverse)
* [user](#user)
* [usertalk](#usertalk)



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
<GorillaBot> Hello, I'm your friendly neighborhood GorillaBot! I perform a number of commands
             that you can view by typing !commands in a private message, or going to
             http://git.io/pNQS6g.
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

### Lang ###
	!lang [code]
	
Looks up the full name of the language from a language code. These are only for languages used on Wikipedia; it is not a comprehensive list of ISO codes.

```irc
<GorillaWarfare> !lang en
<GorillaBot> en is English.
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

### Notify ###
	!notify [nick]
	
Notifies you in private message when a user comes online or returns from away.

```irc
<GorillaWarfare> !notify test_test
<GorillaBot> You will be notified when test_test comes online.
-->| test_test (___@gateway/web/freenode/ip.___) has joined ##GorillaBot
<GorillaBot> test_test has returned.
```

### Reverse ###
	!reverse [language]
	
Looks up the language code from the name of a language. It will return any languages in which the specified language is included.

```irc
<GorillaWarfare> !reverse English
<GorillaBot> English is en, Simple English is simple
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
