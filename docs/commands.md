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

```irc
< GorillaWarfare> !admincommands
< GorillaBot> My available admin commands are join, part, quit, setcommand,
              and unset. See http://molly.github.io/GorillaBot for documentation.
```

Say the available admin-only commands. This does not display command aliases.

### adminlist
    !adminlist

```irc
< GorillaWarfare> !adminlist
< GorillaBot> My bot admin is GorillaWarfare.
```

Say the current bot operators.

### commands
    !commands
    !commandlist

```irc
< GorillaWarfare> !commands
< GorillaBot> My available commands are admincommands, adminlist, commands, hug,
              link, spotify, and xkcd. See http://molly.github.io/GorillaBot
              for documentation.
```

Say the available all-user commands. This does not display command aliases.

### link
    !link URL

```irc
< GorillaWarfare> !link http://molly.github.io/GorillaBot/
< GorillaBot> Link: GorillaBot
< GorillaWarfare> !link https://www.youtube.com/watch?v=aSarf4-REgk
< GorillaBot> Link: "Baby Gorilla Reunites With Mother" (01:43). Uploaded Mar 24,
              2014. 164347 views. 513 likes, 32 dislikes.
```

Provide information about the given link.

In order to provide rich information about YouTube videos, you must provide a YouTube API key when configuring the bot. You can get an API key by registering a project in the [Google Developer Console](https://console.developers.google.com/). Without a key, the normal linking will be used.

#### Settings
* `auto` - All links entered in the chat will be parsed, regardless of whether they're prefaced with `!link`.

### spotify
    !spotify URI

```irc
< GorillaWarfare> !spotify spotify:track:6NmXV4o6bmp704aPGyTVVG
< GorillaBot> "Bøn Fra Helvete (Live)" by Kaizers Orchestra
```

Provide information about the Spotify URI.

#### Settings
* `auto` - All Spotify URIs in the chat will be parsed, regardless of whether they're prefaced with
`!spotify`.

### xkcd
    !xkcd [number|query]
    !relevantxkcd [number|query]

```irc
< GorillaWarfare> !xkcd batman acne
< GorillaBot> xkcd: Complexion: http://xkcd.com/700/
< GorillaWarfare> !xkcd 700
< GorillaBot> xkcd: Complexion: http://xkcd.com/700/
< GorillaWarfare> !xkcd
< GorillaBot> xkcd: Telescope Names: http://xkcd.com/1294/
```

Without any arguments, this provides a random xkcd comic. When a number is supplied, it tries to return the xkcd comic with that given number. When a query string is supplied, it tries to return the xkcd comic that most closely matches that query.