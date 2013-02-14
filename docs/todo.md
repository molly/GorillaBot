# To do

##General
* Reconnect after the bot is disconnected from the server or the socket is closed
  * Failsafe/limit so that if something goes wrong, the bot doesn't repeatedly disconnect and reconnect
* Kill switch in case something does go wrong with the bot
* Allow some modules to be loaded on request
  * Learn new commands?
* Gracefully exit on `KeyboardInterrupt`
* `VERSION` reply
* Check security
* Join channels after identifying to NickServ (to avoid issues with invite-only channels that depend on the cloak)
* Send initialize commands as a response to 004, not immediately
* Hook commands?
* Add API section to config file
* Move string lists, etc. to a data file
* Modularize commands
* Throttle some commands (!help, !command, etc.)
* Only show !help and !command-type commands if they're at the beginning of the sentence
* Allow part and quit commands to display a message as well
* Allow command aliases
* Allow bot admins to be added and removed while the bot is live
    * Store in config file?

##Plugins
###Wikipedia-related
* Return first sentence of Wikipedia article
* Wiktionary definitions
* Language codes
* User info
  * Edit count
  * User rights
  * Wikibirthdays

###Other
* Information about links posted in the channel
  * Reddit
  * YouTube
  * Imgur?
* Calculator
  * Unit conversion
  * Time zone conversion
  * Wolfram?
* Stalk users (find out when the bot last saw them online)
* Translate
* Weather
* Trout, whale, other violent commands
* Banana and/or Batman-related commands
* Read messages for sad/angry/etc.
* Magic 8-ball
* Check if a website is up or down
* Urban Dictionary
