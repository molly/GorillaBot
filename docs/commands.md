# Commanding the bot

The bot receives commands in one of three ways:

1. Detecting a word preceded by an exclamation point: `!command`<br/>
2. Receiving a message addressed to it directly: `GorillaBot: command` or `GorillaBot: !command`<br/>
3. Receving a command in a private message: `/msg GorillaBot command`

In the examples below, I use the `!command` syntax, but the other two would work equally well.

##Commands
###All users
* [commands](#commands)
* [help](#help)
* [hug](#hug)
* [glomp](#hug)
* [link](#link)
* [tacklehug](#hug)
* [user](#user)
* [usertalk](#usertalk)

###Bot admins only
* [join](#join)
* [part](#part)
* [quit](#quit)

## All-user commands ##
### Commands ###
    !commands
    !command
    
Prints the list of all-user commands. Links to this page for further information.

```irc
<GorillaWarfare> !commands
<GorillaBot> I know the following commands: commands, help, hug, link, user,
             usertalk. For further documentation, see http://git.io/pNQS6g
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
    !glomp [user]
    !tacklehug [user]
    
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

### Join ###
    !join #channel
    
Joins the specified channel.

### Part ###

    !part #channel

Parts from the specified channel.
