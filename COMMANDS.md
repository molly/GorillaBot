# Commanding the bot

The bot receives commands in one of three ways:

1. Detecting a word preceded by an exclamation point: `!command`<br/>
2. Receiving a message addressed to it directly: `GorillaBot: command` or `GorillaBot: !command`<br/>
3. Receving a command in a private message: `/msg GorillaBot command`

##Commands
* hug
* glomp
* link
* tacklehug
* user
* usertalk

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
